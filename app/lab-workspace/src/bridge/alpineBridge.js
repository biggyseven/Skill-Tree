import { useLabStore } from '../store/useLabStore.js';

function emit(type, detail) {
  window.dispatchEvent(new CustomEvent(type, { detail }));
  if (window.opener && !window.opener.closed) {
    try { window.opener.postMessage({ type, detail }, window.location.origin); } catch (e) {}
  }
}

let prevSnap = null;

function persistSuccessfulLab(result) {
  if (
    !result ||
    result.passed !== true ||
    result.sandbox === true ||
    result.attempt_recorded !== true ||
    result.stale === true ||
    !result.lab_id
  ) return;

  try {
    const storageKey = 'st:labs-done';
    const saved = JSON.parse(window.localStorage.getItem(storageKey) || '[]');
    const completed = Array.isArray(saved) ? saved.map(String) : [];
    const labId = String(result.lab_id);
    if (!completed.includes(labId)) {
      window.localStorage.setItem(storageKey, JSON.stringify([...completed, labId]));
    }
  } catch (_error) {
    // La progression serveur demeure enregistrée même si le stockage du navigateur est bloqué.
  }
}

export function initAlpineBridge() {
  window.addEventListener('lab:load', (e) => {
    const d = e.detail || {};
    useLabStore.getState().loadLab(d.labId, d.definition, d.initial_topology || d.initialTopology);
  });

  window.addEventListener('lab:check', async () => {
    const initial = useLabStore.getState();
    if (
      !initial.lab || !initial.topology || initial.loading ||
      initial.lab.id === 'demo' ||
      initial.lab.sandbox === true ||
      initial.lab.courseLocked === true ||
      initial.lab.courseLocked === true
    ) return;

    const labId = initial.lab.id;
    const topologySnapshot = JSON.stringify(initial.topology);
    initial.setLoading(true);
    initial.setCheckResult(null);

    const setCurrentCheckResult = (result) => {
      const current = useLabStore.getState();
      const changedDuringCheck =
        current.lab?.id !== labId ||
        JSON.stringify(current.topology) !== topologySnapshot;
      const finalResult = changedDuringCheck
        ? {
            passed: false,
            score: 0,
            stale: true,
            results: [{
              rule_id: 'stale-check',
              passed: false,
              message: 'La topologie a changé pendant la vérification. Relancez le contrôle.',
            }],
          }
        : result;
      current.setCheckResult(finalResult);
      emit('lab:check-result', finalResult);
    };

    try {
      const res = await fetch(`/api/lab/v2/${encodeURIComponent(labId)}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology: initial.topology }),
      });

      if (!res.ok) {
        setCurrentCheckResult({
          passed: false,
          score: 0,
          checkError: true,
          results: [{
            rule_id: 'error',
            passed: false,
            message: `Erreur serveur (${res.status}).`,
          }],
        });
        return;
      }

      setCurrentCheckResult(await res.json());
    } catch (_err) {
      setCurrentCheckResult({
        passed: false,
        score: 0,
        checkError: true,
        results: [{
          rule_id: 'error',
          passed: false,
          message: 'Impossible de joindre le serveur pour vérifier la topologie.',
        }],
      });
    } finally {
      useLabStore.getState().setLoading(false);
    }
  });

  window.addEventListener('lab:submit', async () => {
    const initial = useLabStore.getState();
    const previousCheck = initial.checkResult;
    if (
      !initial.lab ||
      !initial.topology ||
      initial.lab.id === 'demo' ||
      initial.lab.sandbox === true ||
      initial.loading ||
      !previousCheck ||
      previousCheck.stale ||
      previousCheck.checkError ||
      previousCheck.submissionError ||
      previousCheck.ok === true
    ) return;

    const labId = initial.lab.id;
    const topologySnapshot = JSON.stringify(initial.topology);
    initial.setLoading(true);

    try {
      const res = await fetch('/api/lab/v2/' + encodeURIComponent(labId) + '/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology: JSON.parse(topologySnapshot), check_result: previousCheck }),
      });
      const data = await res.json().catch(() => ({}));
      const current = useLabStore.getState();
      const changedDuringSubmit =
        current.lab?.id !== labId ||
        JSON.stringify(current.topology) !== topologySnapshot;

      if (!res.ok) {
        const detail = data.detail || `Erreur serveur (${res.status}).`;
        current.setCheckResult({
          passed: false,
          score: 0,
          checkError: true,
          submissionError: true,
          results: [{ rule_id: 'submit-error', passed: false, message: String(detail) }],
        });
        return;
      }

      const finalResult = changedDuringSubmit
        ? {
            ...data,
            stale: true,
            results: [
              ...(Array.isArray(data.results) ? data.results : []),
              {
                rule_id: 'stale-submission',
                passed: false,
                message: 'La tentative a été enregistrée pour la configuration envoyée, mais la topologie actuelle a changé. Vérifiez-la à nouveau.',
              },
            ],
          }
        : data;
      current.setCheckResult(finalResult);
      persistSuccessfulLab(finalResult);
      emit('lab:submit-result', finalResult);
    } catch (_err) {
      useLabStore.getState().setCheckResult({
        passed: false,
        score: 0,
        checkError: true,
        submissionError: true,
        results: [{
          rule_id: 'submit-error',
          passed: false,
          message: 'Impossible de joindre le serveur pour enregistrer le laboratoire.',
        }],
      });
    } finally {
      useLabStore.getState().setLoading(false);
    }
  });

  window.addEventListener('lab:close', () => {
    useLabStore.setState({ lab: null, topology: null, selectedDevice: null, checkResult: null, error: null });
    emit('lab:closed', {});
    if (window.opener && !window.opener.closed) {
      try { window.close(); return; } catch (e) {}
    }
    // Depuis le même onglet, fermer le lab doit ramener au tableau de bord.
    window.location.assign('/');
  });

  useLabStore.subscribe((state) => {
    const snap = {
      topology: state.topology,
      topologyId: state.topology?.topology_id,
      selectedDevice: state.selectedDevice,
      hasCheck: !!state.checkResult,
    };
    const prev = prevSnap;
    prevSnap = snap;
    if (!prev) return;
    if (snap.topology !== prev.topology || snap.topologyId !== prev.topologyId || snap.selectedDevice !== prev.selectedDevice || snap.hasCheck !== prev.hasCheck) {
      emit('lab:state', { topology: state.topology, selectedDevice: state.selectedDevice });
    }
  });
}