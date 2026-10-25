import { useLabStore } from '../store/useLabStore.js';

function emit(type, detail) {
  window.dispatchEvent(new CustomEvent(type, { detail }));
  if (window.opener && !window.opener.closed) {
    try { window.opener.postMessage({ type, detail }, window.location.origin); } catch (e) {}
  }
}

let prevSnap = null;

export function initAlpineBridge() {
  window.addEventListener('lab:load', (e) => {
    const d = e.detail || {};
    useLabStore.getState().loadLab(d.labId, d.definition, d.initial_topology || d.initialTopology);
  });

  window.addEventListener('lab:check', async () => {
    const st = useLabStore.getState();
    if (!st.lab || !st.topology) return;
    st.setLoading(true);
    st.setCheckResult(null);

    try {
      const res = await fetch(`/api/lab/v2/${st.lab.id}/check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology: st.topology }),
      });
      
      if (!res.ok) {
        // On affiche l'erreur dans le panneau de gauche au lieu de crasher
        st.setCheckResult({ 
          passed: false, score: 0, 
          results: [{ rule_id: 'error', passed: false, message: `Erreur serveur (${res.status}).` }] 
        });
        return;
      }
      
      const result = await res.json();
      st.setCheckResult(result);
      emit('lab:check-result', result);
    } catch (err) {
      st.setCheckResult({ 
        passed: false, score: 0, 
        results: [{ rule_id: 'error', passed: false, message: `Erreur de connexion au serveur.` }] 
      });
    } finally {
      st.setLoading(false);
    }
  });

  window.addEventListener('lab:submit', async () => {
    const st = useLabStore.getState();
    if (!st.lab || !st.topology || st.lab.id === 'demo') return;

    st.setLoading(true);
    try {
      const res = await fetch('/api/lab/v2/' + encodeURIComponent(st.lab.id) + '/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topology: st.topology, check_result: st.checkResult || {} }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const detail = data.detail || `Erreur serveur (${res.status}).`;
        st.setCheckResult({
          passed: false,
          score: 0,
          results: [{ rule_id: 'submit-error', passed: false, message: String(detail) }],
        });
        return;
      }
      st.setCheckResult(data);
      emit('lab:submit-result', data);
    } catch (_err) {
      st.setCheckResult({
        passed: false,
        score: 0,
        results: [{ rule_id: 'submit-error', passed: false, message: 'Impossible de joindre le serveur pour enregistrer le laboratoire.' }],
      });
    } finally {
      st.setLoading(false);
    }
  });

  window.addEventListener('lab:close', () => {
    useLabStore.setState({ lab: null, topology: null, selectedDevice: null, checkResult: null, error: null });
    emit('lab:closed', {});
    if (window.opener && !window.opener.closed) {
      try { window.close(); } catch (e) {}
    }
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