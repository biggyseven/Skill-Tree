import assert from 'node:assert/strict';
import { after, beforeEach, test } from 'node:test';
import { useLabStore } from '../store/useLabStore.js';
import { initAlpineBridge } from './alpineBridge.js';

class FakeCustomEvent {
  constructor(type, options = {}) {
    this.type = type;
    this.detail = options.detail;
  }
}

class FakeWindow {
  constructor() {
    this.location = { origin: 'http://127.0.0.1:8000' };
    this.listeners = new Map();
    this.messages = [];
    this.opener = {
      closed: false,
      postMessage: (message, targetOrigin) => this.messages.push({ message, targetOrigin }),
    };
  }
  addEventListener(type, listener) {
    const listeners = this.listeners.get(type) || [];
    listeners.push(listener);
    this.listeners.set(type, listeners);
  }
  dispatchEvent(event) {
    for (const listener of this.listeners.get(event.type) || []) {
      Promise.resolve(listener(event)).catch(error => {
        queueMicrotask(() => { throw error; });
      });
    }
    return true;
  }
}

const fakeWindow = new FakeWindow();
const originalWindow = globalThis.window;
const originalCustomEvent = globalThis.CustomEvent;
const originalFetch = globalThis.fetch;
globalThis.window = fakeWindow;
globalThis.CustomEvent = FakeCustomEvent;
initAlpineBridge();

function seedLab() {
  useLabStore.getState().loadLab('lab-test', { title: 'Lab de test' }, {
    schema_version: 2,
    topology_id: 'topology-test',
    nodes: [{ id: 'R1', type: 'router', x: 10, y: 20, ports: [] }],
    links: [],
  });
  useLabStore.getState().setCheckResult({ passed: true, score: 1 });
}

async function waitFor(predicate, message) {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    if (predicate()) return;
    await new Promise(resolve => setTimeout(resolve, 0));
  }
  assert.fail(message);
}

beforeEach(() => {
  fakeWindow.messages.length = 0;
  useLabStore.setState({
    lab: null, topology: null, selectedDevice: null, checkResult: null,
    loading: false, error: null, activePacket: null, activeTool: 'select',
  });
  globalThis.fetch = async () => ({
    ok: true,
    status: 200,
    json: async () => ({ passed: true, score: 1, ok: true, attempt_recorded: true }),
  });
});

after(() => {
  if (originalWindow === undefined) delete globalThis.window;
  else globalThis.window = originalWindow;
  if (originalCustomEvent === undefined) delete globalThis.CustomEvent;
  else globalThis.CustomEvent = originalCustomEvent;
  if (originalFetch === undefined) delete globalThis.fetch;
  else globalThis.fetch = originalFetch;
});

test('la vérification transmet la topologie dans le champ attendu par l’API', async () => {
  seedLab();
  let capturedRequest = null;
  globalThis.fetch = async (url, options) => {
    capturedRequest = { url, options };
    return {
      ok: true,
      status: 200,
      json: async () => ({ passed: true, score: 1, results: [] }),
    };
  };

  fakeWindow.dispatchEvent(new CustomEvent('lab:check', { detail: {} }));
  await waitFor(
    () => capturedRequest !== null && useLabStore.getState().loading === false,
    'La vérification de topologie n’a pas reçu sa réponse.',
  );

  assert.equal(capturedRequest.url, '/api/lab/v2/lab-test/check');
  const payload = JSON.parse(capturedRequest.options.body);
  assert.equal(payload.topology.nodes[0].id, 'R1');
  assert.equal(Array.isArray(payload.topology.nodes), true);
  assert.equal(useLabStore.getState().checkResult.passed, true);
});

test('une soumission validée est transmise au dashboard à la même origine', async () => {
  seedLab();
  fakeWindow.dispatchEvent(new CustomEvent('lab:submit', { detail: {} }));

  await waitFor(
    () => fakeWindow.messages.some(item => item.message?.type === 'lab:submit-result'),
    'Le résultat de soumission n’a pas été transmis au dashboard.',
  );

  const posted = fakeWindow.messages.find(item => item.message.type === 'lab:submit-result');
  assert.equal(posted.targetOrigin, fakeWindow.location.origin);
  assert.equal(posted.message.detail.passed, true);
  assert.equal(posted.message.detail.attempt_recorded, true);
  assert.equal(useLabStore.getState().checkResult.ok, true);
  assert.equal(useLabStore.getState().loading, false);
});

test('un bac à sable ne peut pas soumettre une tentative notée', async () => {
  useLabStore.getState().loadLab('node-sandbox', {
    title: 'Workspace libre',
    sandbox: true,
  }, {
    schema_version: 2,
    topology_id: 'sandbox-topology',
    nodes: [],
    links: [],
  });
  useLabStore.getState().setCheckResult({ passed: true, score: 1 });

  let fetchCalls = 0;
  globalThis.fetch = async () => {
    fetchCalls += 1;
    return { ok: true, status: 200, json: async () => ({ passed: true }) };
  };

  fakeWindow.dispatchEvent(new CustomEvent('lab:submit', { detail: {} }));
  await new Promise(resolve => setTimeout(resolve, 0));

  assert.equal(fetchCalls, 0);
  assert.equal(fakeWindow.messages.some(item => item.message?.type === 'lab:submit-result'), false);
  assert.equal(useLabStore.getState().loading, false);
});

test('une réponse serveur en erreur ne remonte pas comme une validation réussie', async () => {
  seedLab();
  globalThis.fetch = async () => ({
    ok: false,
    status: 409,
    json: async () => ({ detail: 'Prérequis manquant' }),
  });

  fakeWindow.dispatchEvent(new CustomEvent('lab:submit', { detail: {} }));
  await waitFor(
    () => useLabStore.getState().loading === false && useLabStore.getState().checkResult?.submissionError === true,
    'L’erreur de soumission n’a pas été conservée dans le workspace.',
  );

  assert.equal(fakeWindow.messages.some(item => item.message?.type === 'lab:submit-result'), false);
  assert.match(useLabStore.getState().checkResult.results[0].message, /Prérequis manquant/);
});

test('une topologie modifiée pendant la soumission est signalée comme obsolète', async () => {
  seedLab();
  let resolveRequest;
  globalThis.fetch = () => new Promise(resolve => { resolveRequest = resolve; });

  fakeWindow.dispatchEvent(new CustomEvent('lab:submit', { detail: {} }));
  await waitFor(() => typeof resolveRequest === 'function', 'La requête de soumission n’a pas été lancée.');

  const current = useLabStore.getState();
  useLabStore.setState(state => ({
    topology: { ...state.topology, topology_id: 'topology-changed-during-submit' },
  }));

  resolveRequest({
    ok: true,
    status: 200,
    json: async () => ({ passed: true, score: 1, ok: true, attempt_recorded: true }),
  });

  await waitFor(
    () => fakeWindow.messages.some(item => item.message?.type === 'lab:submit-result'),
    'Le résultat de soumission n’a pas été transmis après la réponse serveur.',
  );
  const posted = fakeWindow.messages.find(item => item.message.type === 'lab:submit-result');
  assert.equal(posted.message.detail.stale, true);
  assert.match(posted.message.detail.results.at(-1).message, /topologie actuelle a changé/);
});
