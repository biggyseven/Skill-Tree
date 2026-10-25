import { useEffect } from 'react';
import { useLabStore } from './store/useLabStore.js';
import { LabCanvas } from './canvas/LabCanvas.jsx';
import { TopologyToolbar } from './canvas/TopologyToolbar.jsx';
import { BriefPanel } from './brief/BriefPanel.jsx';
import { InspectorPanel } from './inspector/InspectorPanel.jsx';
function fetchLabFromUrl(labId) {
  return fetch('/api/lab/v2/' + labId).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); });
}

export default function App() {
  const lab = useLabStore(s => s.lab);
  const loading = useLabStore(s => s.loading);
  const error = useLabStore(s => s.error);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const labId = params.get('id');
    const demo = params.get('demo');
    if (demo === '1' || !labId) { useLabStore.getState().loadDemo(); return; }
    useLabStore.getState().setLoading(true);
    fetchLabFromUrl(labId)
      .then(data => useLabStore.getState().loadLab(labId, data.definition, data.initial_topology))
      .catch(err => { console.warn('Lab fetch failed, falling back to demo:', err); useLabStore.getState().loadDemo(); });
  }, []);

  if (error) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-[var(--s0)] p-12 text-[var(--text-primary)]">
        <h1 className="mb-4 text-xl font-bold text-[var(--rose-400)]">Erreur</h1>
        <pre className="max-w-2xl whitespace-pre-wrap text-sm text-[var(--text-secondary)]">{error}</pre>
      </div>
    );
  }

  if (loading || !lab) {
    return (
      <div className="flex h-screen items-center justify-center bg-[var(--s0)] text-sm text-[var(--text-muted)]">
        Chargement du Lab Workspace…
      </div>
    );
  }

  return (
    <div className="grid h-screen grid-cols-[300px_1fr_340px] overflow-hidden bg-[var(--s0)] text-[var(--text-primary)]">
      <aside className="overflow-y-auto border-r border-[var(--s2)] bg-[var(--s1)]"><BriefPanel /></aside>
      <main className="flex min-w-0 flex-col">
        <TopologyToolbar />
        <LabCanvas />
      </main>
      <aside className="overflow-hidden border-l border-[var(--s2)] bg-[var(--s1)]">
        <InspectorPanel />
      </aside>
    </div>
  );
}
