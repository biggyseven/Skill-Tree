import { useEffect, useRef, useState } from 'react';
import { useLabStore } from './store/useLabStore.js';
import { LabCanvas } from './canvas/LabCanvas.jsx';
import { TopologyToolbar } from './canvas/TopologyToolbar.jsx';
import { BriefPanel } from './brief/BriefPanel.jsx';
import { TicketPanel } from './brief/TicketPanel.jsx';
import { SLABar } from './war/SLABar.jsx';
import { PostMortemModal } from './war/PostMortemModal.jsx';
import { useTicketStore } from './war/useTicketStore.js';
import { Palette } from './canvas/Palette.jsx';
import { CablePalette } from './canvas/CablePalette.jsx';
import { InspectorPanel } from './inspector/InspectorPanel.jsx';
import { EQUIPMENT_MODEL_COUNT } from './canvas/deviceCatalog.js';
import { CABLES } from './canvas/cableCatalog.js';

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
    <header className="relative z-20 flex h-[64px] shrink-0 items-center justify-between gap-3 border-b border-[var(--lab-border)] bg-[var(--lab-surface)] px-3 shadow-[0_4px_14px_rgba(0,0,0,0.22)] sm:px-4">
      <div className="flex min-w-0 items-center gap-2.5 sm:gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-[var(--lab-accent)]/40 bg-[var(--lab-accent)]/10 font-black tracking-tight text-[var(--lab-accent)]">
          ST
        </div>
        <div className="block min-w-0">
          <div className="text-[9px] font-bold uppercase tracking-[0.13em] text-[var(--lab-text-muted)] sm:text-[10px] sm:tracking-[0.17em]">
            Skill Tree <span className="mx-1 text-[var(--lab-border)]">/</span> Network Lab
          </div>
          <div className="mt-0.5 max-w-[42vw] truncate text-xs font-semibold text-[var(--lab-text)] sm:max-w-[380px] sm:text-sm" title={lab.title}>
            {lab.title || 'Lab Workspace'}
          </div>
        </div>
        <span className="hidden h-7 w-px bg-[var(--lab-border)] lg:block" />
        <div className="hidden min-w-0 lg:block">
          <div className="text-[9px] uppercase tracking-[0.15em] text-[var(--lab-text-muted)]">Topologie</div>
          <div className="mt-0.5 font-mono text-[11px] text-[var(--lab-text-secondary)]">
            {(topology?.nodes || []).length} équipements <span className="text-[var(--lab-text-muted)]">/</span> {(topology?.links || []).length} liaisons
          </div>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
        <span className="hidden rounded-md border border-[var(--lab-border)] bg-[var(--lab-canvas)] px-2.5 py-1.5 text-[10px] font-semibold uppercase tracking-wide text-[var(--lab-text-secondary)] md:inline-flex">
          {level}
        </span>
        <a
          href="/"
          title="Retourner au tableau de bord Skill Tree"
          aria-label="Retour au tableau de bord"
          className="inline-flex h-9 items-center gap-1.5 rounded-md border border-[var(--lab-border)] bg-[var(--lab-canvas)] px-2.5 text-[11px] font-semibold text-[var(--lab-text-secondary)] transition hover:border-[var(--lab-accent)]/70 hover:bg-[var(--lab-accent)]/10 hover:text-white sm:px-3 sm:text-xs"
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
          className="inline-flex h-9 items-center gap-1.5 rounded-md border border-[var(--lab-border)] bg-[var(--lab-canvas)] px-2.5 text-[11px] font-semibold text-[var(--lab-text-secondary)] transition hover:border-[var(--lab-accent)]/70 hover:bg-[var(--lab-accent)]/10 hover:text-white sm:px-3 sm:text-xs"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            {isFullscreen
              ? <><path d="M8 3v5H3" /><path d="M16 3v5h5" /><path d="M8 21v-5H3" /><path d="M16 21v-5h5" /></>
              : <><path d="M8 3H3v5" /><path d="M16 3h5v5" /><path d="M8 21H3v-5" /><path d="M16 21h5v-5" /></>}
          </svg>
          <span className="hidden sm:inline">{isFullscreen ? 'Quitter plein écran' : 'Plein écran'}</span>
        </button>
        <span className="inline-flex h-8 items-center gap-1.5 rounded-md border border-[var(--st-success,#10b981)]/25 bg-[var(--st-success,#10b981)]/[0.07] px-2 text-[9px] font-semibold text-[var(--st-success,#10b981)] sm:h-9 sm:px-2.5 sm:text-[10px]">
          <span className="h-1.5 w-1.5 rounded-full bg-[var(--st-success,#10b981)] shadow-[0_0_6px_rgba(16,185,129,0.65)]" />
          <span className="hidden sm:inline">Lab actif</span>
        </span>
      </div>
    </header>
  );
}

function PanelHeader({ eyebrow, title, detail }) {
  return (
    <header className="flex min-h-[54px] shrink-0 items-center justify-between gap-3 border-b border-[var(--lab-border)] bg-[var(--lab-surface)] px-4 py-3">
      <div className="min-w-0">
        <div className="text-[9px] font-bold uppercase tracking-[0.18em] text-[var(--lab-text-muted)]">{eyebrow}</div>
        <h2 className="mt-1 truncate text-xs font-semibold text-[var(--lab-text)]">{title}</h2>
      </div>
      {detail && <span className="shrink-0 font-mono text-[10px] text-[var(--lab-text-muted)]">{detail}</span>}
    </header>
  );
}

const PANEL_SIZE_STORAGE_KEY = 'skilltree-lab-panel-sizes';
const PANEL_SIZE_LIMITS = {
  left: [240, 520],
  right: [260, 560],
  equipment: [180, 480],
};

function clampPanelSize(key, value, fallback) {
  const limits = PANEL_SIZE_LIMITS[key];
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric) || !limits) return fallback;
  return Math.min(limits[1], Math.max(limits[0], numeric));
}

function readPanelSizes() {
  const fallback = { left: 320, right: 370, equipment: 290 };
  try {
    const saved = JSON.parse(localStorage.getItem(PANEL_SIZE_STORAGE_KEY) || '{}');
    return {
      left: clampPanelSize('left', saved.left, fallback.left),
      right: clampPanelSize('right', saved.right, fallback.right),
      equipment: clampPanelSize('equipment', saved.equipment, fallback.equipment),
    };
  } catch {
    return fallback;
  }
}

export default function App() {
  const lab = useLabStore(s => s.lab);
  const topology = useLabStore(s => s.topology);
  const loading = useLabStore(s => s.loading);
  const error = useLabStore(s => s.error);
  const ticket = useTicketStore(s => s.ticket);
  const [postMortemOpen, setPostMortemOpen] = useState(false);
  const [mobilePane, setMobilePane] = useState('brief');
  const [libraryTab, setLibraryTab] = useState('equipment');
  const [panelSizes, setPanelSizes] = useState(readPanelSizes);
  const resizeRef = useRef(null);

  useEffect(() => {
    const movePointer = (event) => {
      const drag = resizeRef.current;
      if (!drag) return;
      if (drag.type === 'left') {
        setPanelSizes(current => ({
          ...current,
          left: clampPanelSize('left', event.clientX - drag.bounds.left, current.left),
        }));
      } else if (drag.type === 'right') {
        setPanelSizes(current => ({
          ...current,
          right: clampPanelSize('right', drag.bounds.right - event.clientX, current.right),
        }));
      } else if (drag.type === 'equipment') {
        setPanelSizes(current => ({
          ...current,
          equipment: clampPanelSize('equipment', drag.bounds.bottom - event.clientY, current.equipment),
        }));
      }
    };
    const stopPointer = () => {
      resizeRef.current = null;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
    window.addEventListener('pointermove', movePointer);
    window.addEventListener('pointerup', stopPointer);
    window.addEventListener('pointercancel', stopPointer);
    return () => {
      window.removeEventListener('pointermove', movePointer);
      window.removeEventListener('pointerup', stopPointer);
      window.removeEventListener('pointercancel', stopPointer);
      stopPointer();
    };
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(PANEL_SIZE_STORAGE_KEY, JSON.stringify(panelSizes));
    } catch {
      // Le redimensionnement reste disponible même si le stockage est désactivé.
    }
  }, [panelSizes]);

  function beginResize(event, type) {
    event.preventDefault();
    const boundsElement = event.currentTarget.parentElement;
    if (!boundsElement) return;
    resizeRef.current = { type, bounds: boundsElement.getBoundingClientRect() };
    document.body.style.cursor = type === 'equipment' ? 'row-resize' : 'col-resize';
    document.body.style.userSelect = 'none';
  }

  function resizeWithKeyboard(event, type) {
    const directions = type === 'equipment'
      ? { ArrowUp: 16, ArrowDown: -16 }
      : type === 'left'
        ? { ArrowLeft: -16, ArrowRight: 16 }
        : { ArrowLeft: 16, ArrowRight: -16 };
    const delta = directions[event.key];
    if (!delta) return;
    event.preventDefault();
    setPanelSizes(current => ({
      ...current,
      [type]: clampPanelSize(type, current[type] + delta, current[type]),
    }));
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const ticketId = params.get('ticket');
    if (ticketId) {
      useLabStore.getState().setLoading(true);
      fetch('/api/tickets/' + encodeURIComponent(ticketId))
        .then(async response => {
          const payload = await response.json().catch(() => ({}));
          if (!response.ok) throw new Error(payload.detail || 'HTTP ' + response.status);
          return payload;
        })
        .then(({ ticket: loadedTicket, scenario }) => {
          useTicketStore.getState().setTicket(loadedTicket, scenario, loadedTicket.sla_left);
          if (loadedTicket.status === 'pending_postmortem') setPostMortemOpen(true);
          useLabStore.getState().loadLab(loadedTicket.id, {
            title: scenario.title, level: 'War Room', module: 'ITSM / NOC',
            prompt: scenario.story, objectives: (scenario.diagnostic_steps || []).map(step => step.title),
            hints: [], xp_reward: scenario.reward_xp || 0, badges: [], ticketMode: true,
          }, scenario.initial_topology);
        })
        .catch(err => {
          console.error('War Room ticket could not load:', err);
          useTicketStore.getState().clearTicket();
          useLabStore.getState().setError(new Error('Impossible de charger le ticket "' + ticketId + '". Détail : ' + err.message));
        });
      return;
    }
    useTicketStore.getState().clearTicket();
    setPostMortemOpen(false);
    const labId = params.get('id');
    const demo = params.get('demo');
    if (demo === '1') {
      useLabStore.getState().loadDemo();
      return;
    }
    if (!labId) {
      useLabStore.getState().loadFreeWorkspace();
      return;
    }

    useLabStore.getState().setLoading(true);
    fetchLabFromUrl(labId)
      .then(data => useLabStore.getState().loadLab(labId, {
        ...(data.definition || {}),
        sandbox: data.sandbox === true,
        courseLocked: data.course_locked === true,
        courseLockMessage: data.course_lock_message || '',
      }, data.initial_topology))
      .catch(err => {
        console.error('Lab Workspace could not load the requested lab:', err);
        useLabStore.getState().setError(
          new Error(`Impossible de charger le laboratoire "${labId}". Vérifiez que cet identifiant possède un scénario configuré et que l'API est disponible. Détail : ${err.message}`)
        );
      });
  }, []);

  if (error) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-[var(--lab-canvas)] p-8 text-[var(--lab-text)]">
        <div className="w-full max-w-2xl rounded-xl border border-[var(--lab-danger,#f85149)]/30 bg-[var(--lab-surface)] p-6">
          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.18em] text-[var(--lab-danger,#f85149)]">Erreur de chargement</div>
          <h1 className="mb-3 text-lg font-semibold">Le Lab Workspace n'a pas pu s'ouvrir</h1>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--lab-text-secondary)]">{error}</pre>
        </div>
      </div>
    );
  }

  if (loading || !lab) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-3 bg-[var(--lab-canvas)] text-sm text-[var(--lab-text-muted)]">
        <span className="h-7 w-7 animate-spin rounded-full border-2 border-[var(--lab-border)] border-t-[#0ea5e9]" />
        Chargement du Lab Workspace…
      </div>
    );
  }

  return (
    <div className="flex h-screen min-h-0 flex-col overflow-hidden bg-[var(--lab-canvas)] text-[var(--lab-text)]">
      <WorkspaceHeader lab={lab} topology={topology} />

      <nav className="grid grid-cols-3 gap-1 border-b border-[var(--lab-border)] bg-[var(--lab-canvas)] p-1.5 xl:hidden" aria-label="Panneaux du laboratoire">
        <button
          type="button"
          onClick={() => setMobilePane('brief')}
          aria-current={mobilePane === 'brief' ? 'page' : undefined}
          className={mobilePane === 'brief'
            ? 'min-h-11 rounded-lg border border-[var(--lab-accent)]/40 bg-[var(--lab-accent)]/15 px-2 py-2 text-xs font-semibold text-[var(--lab-accent)]'
            : 'min-h-11 rounded-lg border border-transparent px-2 py-2 text-xs font-medium text-[var(--lab-text-muted)] hover:bg-[var(--lab-surface)] hover:text-[var(--lab-text)]'}
        >
          <span className="mr-1.5 font-mono text-[10px]">01</span>Mission
        </button>
        <button
          type="button"
          onClick={() => setMobilePane('canvas')}
          aria-current={mobilePane === 'canvas' ? 'page' : undefined}
          className={mobilePane === 'canvas'
            ? 'min-h-11 rounded-lg border border-[var(--lab-accent)]/40 bg-[var(--lab-accent)]/15 px-2 py-2 text-xs font-semibold text-[var(--lab-accent)]'
            : 'min-h-11 rounded-lg border border-transparent px-2 py-2 text-xs font-medium text-[var(--lab-text-muted)] hover:bg-[var(--lab-surface)] hover:text-[var(--lab-text)]'}
        >
          <span className="mr-1.5 font-mono text-[10px]">02</span>Topologie
        </button>
        <button
          type="button"
          onClick={() => setMobilePane('inspector')}
          aria-current={mobilePane === 'inspector' ? 'page' : undefined}
          className={mobilePane === 'inspector'
            ? 'min-h-11 rounded-lg border border-[var(--lab-accent)]/40 bg-[var(--lab-accent)]/15 px-2 py-2 text-xs font-semibold text-[var(--lab-accent)]'
            : 'min-h-11 rounded-lg border border-transparent px-2 py-2 text-xs font-medium text-[var(--lab-text-muted)] hover:bg-[var(--lab-surface)] hover:text-[var(--lab-text)]'}
        >
          <span className="mr-1.5 font-mono text-[10px]">03</span>Console
        </button>
      </nav>

      <div
        className="flex min-h-0 flex-1 overflow-hidden"
        style={{
          '--lab-left-width': `${panelSizes.left}px`,
          '--lab-right-width': `${panelSizes.right}px`,
          '--lab-equipment-height': `${panelSizes.equipment}px`,
        }}
      >
        {/* Panneau gauche : mission pédagogique et bibliothèque matérielle */}
        <aside data-testid="lab-left-panel" className={`${mobilePane === 'brief' ? 'flex' : 'hidden xl:flex'} w-full min-w-0 flex-col overflow-hidden border-r border-[var(--lab-border)] bg-[var(--lab-surface)] xl:w-[var(--lab-left-width)] xl:shrink-0`}>
          <section className="flex min-h-0 flex-1 flex-col">
            <PanelHeader eyebrow={ticket ? "01 / War Room" : "01 / Lab brief"} title={ticket ? "Ticket ITSM" : "Mission & objectifs"} />
            <div className="lab-scrollbar min-h-0 flex-1 overflow-y-auto">
              {ticket ? <TicketPanel /> : <BriefPanel />}
            </div>
          </section>

          <div
            role="separator"
            aria-orientation="horizontal"
            aria-label="Redimensionner les bibliothèques d’équipements et de câbles"
            title="Glisser pour redimensionner les bibliothèques d’équipements et de câbles"
            tabIndex={0}
            onPointerDown={event => beginResize(event, 'equipment')}
            onKeyDown={event => resizeWithKeyboard(event, 'equipment')}
            className="hidden h-2 shrink-0 cursor-row-resize touch-none items-center justify-center bg-[var(--lab-border)] transition-colors hover:bg-[var(--lab-accent)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--lab-accent)] xl:flex"
          >
            <span className="h-0.5 w-10 rounded-full bg-[var(--lab-text-muted)]" />
          </div>
          <section data-testid="equipment-palette-panel" className="flex h-[var(--lab-equipment-height)] shrink-0 flex-col overflow-hidden border-t border-[var(--lab-border)] bg-[var(--lab-canvas)]/50">
            <div data-library-tabs role="tablist" aria-label="Bibliothèques du laboratoire" className="grid shrink-0 grid-cols-2 gap-1 border-b border-[var(--lab-border)] bg-[var(--lab-surface)] p-1.5">
              <button
                id="lab-equipment-tab"
                type="button"
                role="tab"
                data-library-tab="equipment"
                aria-controls="lab-library-panel"
                aria-selected={libraryTab === 'equipment'}
                onClick={() => setLibraryTab('equipment')}
                className={libraryTab === 'equipment'
                  ? 'flex min-h-10 items-center justify-center gap-2 rounded-md border border-[var(--lab-accent)]/40 bg-[var(--lab-accent)]/15 px-2 text-[11px] font-semibold text-[var(--lab-accent)]'
                  : 'flex min-h-10 items-center justify-center gap-2 rounded-md border border-transparent px-2 text-[11px] font-medium text-[var(--lab-text-muted)] hover:bg-[var(--lab-canvas)] hover:text-[var(--lab-text)]'}
              >
                <span aria-hidden="true">▦</span>
                Équipements
                <span className="rounded border border-current/20 px-1 py-0.5 text-[9px]">{EQUIPMENT_MODEL_COUNT} modèles</span>
              </button>
              <button
                id="lab-cables-tab"
                type="button"
                role="tab"
                data-library-tab="cables"
                aria-controls="lab-library-panel"
                aria-selected={libraryTab === 'cables'}
                onClick={() => setLibraryTab('cables')}
                className={libraryTab === 'cables'
                  ? 'flex min-h-10 items-center justify-center gap-2 rounded-md border border-[var(--lab-accent)]/40 bg-[var(--lab-accent)]/15 px-2 text-[11px] font-semibold text-[var(--lab-accent)]'
                  : 'flex min-h-10 items-center justify-center gap-2 rounded-md border border-transparent px-2 text-[11px] font-medium text-[var(--lab-text-muted)] hover:bg-[var(--lab-canvas)] hover:text-[var(--lab-text)]'}
              >
                <span aria-hidden="true">⟷</span>
                Câbles
                <span className="rounded border border-current/20 px-1 py-0.5 text-[9px]">{CABLES.length} câbles</span>
              </button>
            </div>
            <div id="lab-library-panel" role="tabpanel" aria-labelledby={libraryTab === 'equipment' ? 'lab-equipment-tab' : 'lab-cables-tab'} className="min-h-0 flex-1 overflow-hidden">
              {libraryTab === 'equipment' ? <Palette /> : <CablePalette />}
            </div>
          </section>
        </aside>

        <div
          role="separator"
          aria-orientation="vertical"
          aria-label="Redimensionner le panneau gauche"
          title="Glisser pour redimensionner le panneau gauche"
          tabIndex={0}
          onPointerDown={event => beginResize(event, 'left')}
          onKeyDown={event => resizeWithKeyboard(event, 'left')}
          className="hidden w-2 shrink-0 cursor-col-resize touch-none items-center justify-center bg-[var(--lab-border)] transition-colors hover:bg-[var(--lab-accent)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--lab-accent)] xl:flex"
        >
          <span className="h-10 w-0.5 rounded-full bg-[var(--lab-text-muted)]" />
        </div>

        {/* Canvas central : la zone de travail principale */}
        <main className={`${mobilePane === 'canvas' ? 'flex' : 'hidden xl:flex'} w-full min-w-0 flex-1 flex-col overflow-hidden bg-[var(--lab-canvas)] xl:w-auto`}>
          {ticket && <SLABar />}
          <TopologyToolbar onOpenPostMortem={() => setPostMortemOpen(true)} />
          <LabCanvas />
        </main>

        <div
          role="separator"
          aria-orientation="vertical"
          aria-label="Redimensionner le panneau droit"
          title="Glisser pour redimensionner le panneau droit"
          tabIndex={0}
          onPointerDown={event => beginResize(event, 'right')}
          onKeyDown={event => resizeWithKeyboard(event, 'right')}
          className="hidden w-2 shrink-0 cursor-col-resize touch-none items-center justify-center bg-[var(--lab-border)] transition-colors hover:bg-[var(--lab-accent)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[var(--lab-accent)] xl:flex"
        >
          <span className="h-10 w-0.5 rounded-full bg-[var(--lab-text-muted)]" />
        </div>

        {/* Panneau droit : console CLI et inspection matérielle */}
        <aside data-testid="lab-right-panel" className={`${mobilePane === 'inspector' ? 'flex' : 'hidden xl:flex'} w-full min-w-0 flex-col overflow-hidden border-l border-[var(--lab-border)] bg-[var(--lab-surface)] xl:w-[var(--lab-right-width)] xl:shrink-0`}>
          <InspectorPanel />
        </aside>
      </div>
      {ticket && postMortemOpen && <PostMortemModal onClose={() => setPostMortemOpen(false)} />}
    </div>
  );
}
