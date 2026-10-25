import { useLabStore } from '../store/useLabStore.js';

export function Toolbar() {
  const activeTool = useLabStore(s => s.activeTool);
  const setTool = useLabStore(s => s.setTool);

  const tools = [
    { id: 'select', icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"></path><path d="M13 13l6 6"></path></svg>
    ), label: 'Sélectionner' },
    { id: 'cable_straight', icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" strokeWidth="2" strokeLinecap="round"><path d="M4 12h16M4 12l4-4m-4 4l4 4m12-4l-4-4m4 4l-4 4"></path></svg>
    ), label: 'Câble Droit' },
    { id: 'cable_cross', icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#f97316" strokeWidth="2" strokeLinecap="round" strokeDasharray="2 2"><path d="M4 12h16M4 12l4-4m-4 4l4 4m12-4l-4-4m4 4l-4 4"></path></svg>
    ), label: 'Câble Croisé' },
    { id: 'fiber', icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="#a855f7" strokeWidth="2" strokeLinecap="round"><path d="M4 12h16M4 12l4-4m-4 4l4 4m12-4l-4-4m4 4l-4 4"></path></svg>
    ), label: 'Fibre Optique' },
  ];

  return (
    <div className="absolute bottom-6 left-1/2 z-50 flex -translate-x-1/2 items-center gap-1 rounded-xl border border-[#334155] bg-[#0d1117]/90 p-1.5 shadow-2xl backdrop-blur-md">
      {tools.map(t => (
        <button
          key={t.id}
          onClick={() => setTool(t.id)}
          title={t.label}
          className={`flex h-10 w-10 items-center justify-center rounded-lg transition-all ${activeTool === t.id ? 'bg-[#1e293b] text-white shadow-inner border border-[#334155]' : 'text-[#64748b] hover:bg-[#1e293b] hover:text-[#e2e8f0]'}`}
        >
          <div className="h-5 w-5">{t.icon}</div>
        </button>
      ))}
    </div>
  );
}
