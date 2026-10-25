import { useEffect, useState } from 'react';
import { useLabStore } from './store/useLabStore.js';
import { LabCanvas } from './canvas/LabCanvas.jsx';
import { TopologyToolbar } from './canvas/TopologyToolbar.jsx';
import { BriefPanel } from './brief/BriefPanel.jsx';
import { Palette } from './canvas/Palette.jsx';
import { InspectorPanel } from './inspector/InspectorPanel.jsx';

function fetchLabFromUrl(labId) {
  return fetch('/api/lab/v2/' + encodeURIComponent(labId)).then(async response => {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || 'HTTP ' + response.status);
    }
    return payload;
  });
}

function WorkspaceHeader({ lab, topology }) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const levelLabels = {
    debutant: 'Débutant',
    intermediaire: 'Intermédiaire',
    expert: 'Expert',
  };
  const level = levelLabels[String(lab.level || '').toLowerCase()] || lab.level || 'Lab';

  useEffect(() => {
    const updateFullscreen = () => setIsFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener('fullscreenchange', updateFullscreen);
    updateFullscreen();
    return () => document.removeEventListener('fullscreenchange', updateFullscreen);
  }, []);

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen();
      } else {
        await document.documentElement.requestFullscreen();
      }
    } catch (error) {
      console.warn('Le mode plein écran n’est pas disponible dans ce navigateur.', error);
    }
  }

  return (
    <header className="relative z-20 flex h-[64px] shrink-0 items-center justify-between gap-3 border-b border-[#30363d] bg-[#161b22] px-3 shadow-[0_4px_14px_rgba(0,0,0,0.22)] sm:px-4">
      <div className="flex min-w-0 items-center gap-2.5 sm:gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-[#0ea5e9]/40 bg-[#0ea5e9]/10 font-black tracking-tight text-[#38bdf8]">
          ST
        </div>
        <div className="block min-w-0">
          <div className="text-[9px] font-bold uppercase tracking-[0.13em] text-[#8b949e] sm:text-[10px] sm:tracking-[0.17em]">
            Skill Tree <span className="mx-1 text-[#30363d]">/</span> Network Lab
          </div>
          <div className="mt-0.5 max-w-[42vw] truncate text-xs font-semibold text-[#e6edf3] sm:max-w-[380px] sm:text-sm" title={lab.title}>
            {lab.title || 'Lab Workspace'}
          </div>
        </div>
        <span className="hidden h-7 w-px bg-[#30363d] lg:block" />
        <div className="hidden min-w-0 lg:block">
          <div className="text-[9px] uppercase tracking-[0.15em] text-[#6e7681]">Topologie</div>
          <div className="mt-0.5 font-mono text-[11px] text-[#c9d1d9]">
            {(topology?.nodes || []).length} équipements <span className="text-[#484f58]">/</span> {(topology?.links || []).length} liaisons
          </div>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
        <span className="hidden rounded-md border border-[#30363d] bg-[#0d1117] px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-wide text-[#c9d1d9] md:inline-flex">
          {level}
        </span>
        <a
          href="/"
          title="Retourner au tableau de bord Skill Tree"
          aria-label="Retour au tableau de bord"
          className="inline-flex h-9 items-center gap-1.5 rounded-md border border-[#30363d] bg-[#0d1117] px-2.5 text-[11px] font-semibold text-[#c9d1d9] transition hover:border-[#0ea5e9]/70 hover:bg-[#0ea5e9]/10 hover:text-white sm:px-3 sm:text-xs"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="m3 10 9-7 9 7" /><path d="M5 9v12h14V9" /><path d="M9 21v-7h6v7" />
          </svg>
          <span className="hidden sm:inline">Tableau de bord</span>
        </a>
        <button
          type="button"
          onClick={toggleFullscreen}
          title={isFullscreen ? 'Quitter le plein écran' : 'Passer en plein écran'}
          aria-label={isFullscreen ? 'Quitter le plein écran' : 'Passer en plein écran'}
          className="inline-flex h-9 items-center gap-1.5 rounded-md border border-[#30363d] bg-[#0d1117] px-2.5 text-[11px] font-semibold text-[#c9d1d9] transition hover:border-[#0ea5e9]/70 hover:bg-[#0ea5e9]/10 hover:text-white sm:px-3 sm:text-xs"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            {isFullscreen
              ? <><path d="M8 3v5H3" /><path d="M16 3v5h5" /><path d="M8 21v-5H3" /><path d="M16 21v-5h5" /></>
              : <><path d="M8 3H3v5" /><path d="M16 3h5v5" /><path d="M8 21H3v-5" /><path d="M16 21h5v-5" /></>}
          </svg>
          <span className="hidden sm:inline">{isFullscreen ? 'Quitter plein écran' : 'Plein écran'}</span>
        </button>
        <span className="inline-flex h-8 items-center gap-1.5 rounded-md border border-[#10b981]/25 bg-[#10b981]/[0.07] px-2 text-[9px] font-semibold text-[#10b981] sm:h-9 sm:px-2.5 sm:text-[10px]">
          <span className="h-1.5 w-1.5 rounded-full bg-[#10b981] shadow-[0_0_6px_rgba(16,185,129,0.65)]" />
          <span className="hidden sm:inline">Lab actif</span>
        </span>
      </div>
    </header>
  );
}

function PanelHeader({ eyebrow, title, detail }) {
  return (
    <header className="flex min-h-[54px] shrink-0 items-center justify-between gap-3 border-b border-[#30363d] bg-[#161b22] px-4 py-3">
      <div className="min-w-0">
        <div className="text-[9px] font-bold uppercase tracking-[0.18em] text-[#6e7681]">{eyebrow}</div>
        <h2 className="mt-1 truncate text-xs font-semibold text-[#e6edf3]">{title}</h2>
      </div>
      {detail && <span className="shrink-0 font-mono text-[10px] text-[#8b949e]">{detail}</span>}
    </header>
  );
}

export default function App() {
  const lab = useLabStore(s => s.lab);
  const topology = useLabStore(s => s.topology);
  const loading = useLabStore(s => s.loading);
  const error = useLabStore(s => s.error);
  const [mobilePane, setMobilePane] = useState('canvas');

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const labId = params.get('id');
    const demo = params.get('demo');
    if (demo === '1' || !labId) {
      useLabStore.getState().loadDemo();
      return;
    }

    useLabStore.getState().setLoading(true);
    fetchLabFromUrl(labId)
      .then(data => useLabStore.getState().loadLab(labId, data.definition, data.initial_topology))
      .catch(err => {
        console.error('Lab Workspace could not load the requested lab:', err);
        useLabStore.getState().setError(
          new Error(`Impossible de charger le lab "${labId}". Vérifiez que la migration M1 a été exécutée et que l'API est disponible. Détail : ${err.message}`)
        );
      });
  }, []);

  if (error) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-[#0d1117] p-8 text-[#e6edf3]">
        <div className="w-full max-w-2xl rounded-xl border border-[#f85149]/30 bg-[#161b22] p-6">
          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[#f85149]">Erreur de chargement</div>
          <h1 className="mb-3 text-lg font-semibold">Le Lab Workspace n'a pas pu s'ouvrir</h1>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-[#c9d1d9]">{error}</pre>
        </div>
      </div>
    );
  }

  if (loading || !lab) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 bg-[#0d1117] text-sm text-[#8b949e]">
        <span className="h-7 w-7 animate-spin rounded-full border-2 border-[#30363d] border-t-[#0ea5e9]" />
        Chargement du Lab Workspace…
      </div>
    );
  }

  return (
    <div className="flex h-screen min-h-0 flex-col overflow-hidden bg-[#0d1117] text-[#e6edf3]">
      <WorkspaceHeader lab={lab} topology={topology} />

      <nav className="grid grid-cols-3 gap-1 border-b border-[#30363d] bg-[#0d1117] p-1.5 xl:hidden" aria-label="Panneaux du laboratoire">
        <button
          type="button"
          onClick={() => setMobilePane('brief')}
          aria-current={mobilePane === 'brief' ? 'page' : undefined}
          className={mobilePane === 'brief'
            ? 'min-h-11 rounded-lg border border-[#0ea5e9]/40 bg-[#0ea5e9]/15 px-2 py-2 text-xs font-semibold text-[#7dd3fc]'
            : 'min-h-11 rounded-lg border border-transparent px-2 py-2 text-xs font-medium text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]'}
        >
          <span className="mr-1.5 font-mono text-[10px]">01</span>Mission
        </button>
        <button
          type="button"
          onClick={() => setMobilePane('canvas')}
          aria-current={mobilePane === 'canvas' ? 'page' : undefined}
          className={mobilePane === 'canvas'
            ? 'min-h-11 rounded-lg border border-[#0ea5e9]/40 bg-[#0ea5e9]/15 px-2 py-2 text-xs font-semibold text-[#7dd3fc]'
            : 'min-h-11 rounded-lg border border-transparent px-2 py-2 text-xs font-medium text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]'}
        >
          <span className="mr-1.5 font-mono text-[10px]">02</span>Topologie
        </button>
        <button
          type="button"
          onClick={() => setMobilePane('inspector')}
          aria-current={mobilePane === 'inspector' ? 'page' : undefined}
          className={mobilePane === 'inspector'
            ? 'min-h-11 rounded-lg border border-[#0ea5e9]/40 bg-[#0ea5e9]/15 px-2 py-2 text-xs font-semibold text-[#7dd3fc]'
            : 'min-h-11 rounded-lg border border-transparent px-2 py-2 text-xs font-medium text-[#8b949e] hover:bg-[#161b22] hover:text-[#e6edf3]'}
        >
          <span className="mr-1.5 font-mono text-[10px]">03</span>Console
        </button>
      </nav>

      <div className="flex min-h-0 flex-1 overflow-hidden">
        {/* Panneau gauche : mission pédagogique et bibliothèque matérielle */}
        <aside className={`${mobilePane === 'brief' ? 'flex' : 'hidden xl:flex'} w-full min-w-0 flex-col overflow-hidden border-r border-[#30363d] bg-[#161b22] xl:w-[320px] xl:shrink-0`}>
          <section className="flex min-h-0 flex-1 flex-col">
            <PanelHeader eyebrow="01 / Lab brief" title="Mission & objectifs" />
            <div className="lab-scrollbar min-h-0 flex-1 overflow-y-auto">
              <BriefPanel />
            </div>
          </section>

          <section className="flex h-[290px] shrink-0 flex-col border-t border-[#30363d] bg-[#0d1117]/50">
            <PanelHeader eyebrow="02 / Device library" title="Bibliothèque d'équipements" />
            <div className="min-h-0 flex-1 overflow-hidden">
              <Palette />
            </div>
          </section>
        </aside>

        {/* Canvas central : la zone de travail principale */}
        <main className={`${mobilePane === 'canvas' ? 'flex' : 'hidden xl:flex'} w-full min-w-0 flex-1 flex-col overflow-hidden bg-[#0d1117] xl:w-auto`}>
          <TopologyToolbar />
          <LabCanvas />
        </main>

        {/* Panneau droit : console CLI et inspection matérielle */}
        <aside className={`${mobilePane === 'inspector' ? 'flex' : 'hidden xl:flex'} w-full min-w-0 flex-col overflow-hidden border-l border-[#30363d] bg-[#161b22] xl:w-[370px] xl:shrink-0`}>
          <InspectorPanel />
        </aside>
      </div>
    </div>
  );
}
