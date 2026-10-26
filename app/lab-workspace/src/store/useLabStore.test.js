import assert from 'node:assert/strict';
import { beforeEach, test } from 'node:test';
import { useLabStore } from './useLabStore.js';

function makeTopology() {
  const port = (id) => ({ id, name: id, state: 'down', ip: null, mask: null });
  const device = (id) => ({
    id, type: 'router', x: 100, y: 100, label: id,
    ports: [port('Fa0/0'), port('Fa0/1')],
    config: { hostname: id, ospf: { enabled: false, areas: [] }, routes: [], vlans: [] },
  });
  return {
    schema_version: 2, topology_id: 'test-topology',
    metadata: { name: 'Test', author: 'test', created_at: '2026-01-01T00:00:00Z', mode: 'lab' },
    nodes: [device('R1'), device('R2')], links: [],
    simulation: { state: 'idle', event_log: [] },
  };
}

function seedCheckedLab() {
  useLabStore.getState().loadLab('lab-test', { title: 'Lab de test' }, makeTopology());
  useLabStore.getState().setCheckResult({ passed: true, score: 1 });
}

beforeEach(() => useLabStore.setState({
  lab: null, topology: null, selectedDevice: null, checkResult: null,
  loading: false, error: null, activePacket: null, activeTool: 'select',
}));

test('les changements de configuration invalident le contrôle précédent', () => {
  seedCheckedLab();
  useLabStore.getState().addNode('router', 200, 200);
  assert.equal(useLabStore.getState().checkResult, null);

  seedCheckedLab();
  useLabStore.getState().addPort('R1');
  assert.equal(useLabStore.getState().checkResult, null);

  seedCheckedLab();
  useLabStore.getState().togglePortState('R1', 'Fa0/0');
  assert.equal(useLabStore.getState().checkResult, null);

  seedCheckedLab();
  useLabStore.getState().removePort('R1', 'Fa0/1');
  assert.equal(useLabStore.getState().checkResult, null);

  seedCheckedLab();
  useLabStore.getState().addLink({
    source: 'R1', target: 'R2', sourceHandle: 'Fa0/0', targetHandle: 'Fa0/0',
  }, 'cable_straight');
  assert.equal(useLabStore.getState().checkResult, null);
});

test('la configuration IPv4 d’un port est enregistrée et invalide le contrôle précédent', () => {
  seedCheckedLab();
  useLabStore.getState().updatePortAddress('R1', 'Fa0/0', '192.168.10.10', '255.255.255.0');

  const state = useLabStore.getState();
  const port = state.topology.nodes.find(node => node.id === 'R1').ports.find(item => item.id === 'Fa0/0');
  assert.equal(port.ip, '192.168.10.10');
  assert.equal(port.mask, '255.255.255.0');
  assert.equal(state.checkResult, null);
});

test('déplacer un équipement conserve le résultat car la position n’est pas la configuration', () => {
  seedCheckedLab();
  useLabStore.getState().updateNodePosition('R1', 360, 220);
  assert.deepEqual(useLabStore.getState().checkResult, { passed: true, score: 1 });
});

test('le workspace ouvert sans identifiant démarre vide et non noté', () => {
  useLabStore.getState().loadFreeWorkspace();
  const state = useLabStore.getState();
  assert.equal(state.lab.id, 'workspace-libre');
  assert.equal(state.lab.sandbox, true);
  assert.equal(state.lab.title, 'Espace de travail libre');
  assert.deepEqual(state.topology.nodes, []);
  assert.deepEqual(state.topology.links, []);
  assert.equal(state.topology.metadata.name, 'Espace de travail libre');
});

test('un scenario canonique conserve l’identifiant du cours demandé', () => {
  useLabStore.getState().loadLab('ipv4-debutant', { id: 'ipv4', title: 'Adressage IPv4' }, makeTopology());
  assert.equal(useLabStore.getState().lab.id, 'ipv4-debutant');
});

test('les actions matérielles restent sûres avant le chargement d’un lab', () => {
  assert.doesNotThrow(() => useLabStore.getState().removePort('R1', 'Fa0/0'));
  assert.doesNotThrow(() => useLabStore.getState().togglePortState('R1', 'Fa0/0'));
  assert.equal(useLabStore.getState().topology, null);
});
