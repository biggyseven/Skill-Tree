import React from 'react';

export function DeviceIcon({ type, className }) {
  const baseClass = className || "w-10 h-10";
  
  switch (type) {
    case 'router':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><circle cx="24" cy="24" r="20" fill="#1e3a8a" stroke="#3b82f6" strokeWidth="1.5"/><path d="M12 24h8m8 0h8M20 24l4-4m-4 4l4 4m4-4l-4-4m4 4l-4 4" stroke="#60a5fa" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M16 16h4v16h-4z" fill="#1e3a8a" stroke="#3b82f6"/><circle cx="38" cy="16" r="1.5" fill="#22c55e"/><circle cx="38" cy="32" r="1.5" fill="#ef4444"/></svg>);
    case 'switch':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><rect x="6" y="16" width="36" height="16" rx="2" fill="#0f172a" stroke="#94a3b8" strokeWidth="1.5"/><path d="M10 22h2m2 0h2m2 0h2m2 0h2m2 0h2m2 0h2m2 0h2" stroke="#22c55e" strokeWidth="2" strokeLinecap="round"/><path d="M10 26h2m2 0h2m2 0h2m2 0h2m2 0h2m2 0h2m2 0h2" stroke="#eab308" strokeWidth="2" strokeLinecap="round"/><rect x="14" y="32" width="20" height="4" rx="1" fill="#1e293b"/></svg>);
    case 'pc':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><rect x="10" y="8" width="28" height="20" rx="2" fill="#1e293b" stroke="#64748b" strokeWidth="1.5"/><rect x="12" y="10" width="24" height="16" fill="#0ea5e9" opacity="0.2"/><path d="M22 28v6m-6 0h12m-14 4h16" stroke="#64748b" strokeWidth="2" strokeLinecap="round"/><rect x="16" y="34" width="16" height="6" rx="1" fill="#334155"/></svg>);
    case 'server':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><rect x="12" y="8" width="24" height="32" rx="2" fill="#0f172a" stroke="#64748b" strokeWidth="1.5"/><rect x="16" y="12" width="16" height="6" rx="1" fill="#1e293b" stroke="#475569"/><rect x="16" y="21" width="16" height="6" rx="1" fill="#1e293b" stroke="#475569"/><rect x="16" y="30" width="16" height="6" rx="1" fill="#1e293b" stroke="#475569"/><circle cx="20" cy="15" r="1" fill="#22c55e"/><circle cx="20" cy="24" r="1" fill="#eab308"/><circle cx="20" cy="33" r="1" fill="#3b82f6"/></svg>);
    case 'firewall':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><rect x="8" y="10" width="32" height="28" rx="2" fill="#450a0a" stroke="#ef4444" strokeWidth="1.5"/><path d="M8 18h32M8 26h32M8 34h32M20 10v8M28 18v8M20 26v8" stroke="#ef4444" strokeWidth="1.5"/><path d="M24 22l4 4m0-4l-4 4" stroke="#fca5a5" strokeWidth="2" strokeLinecap="round"/></svg>);
    case 'cloud':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><path d="M16 34h16a8 8 0 000-16 12 12 0 00-22-2 8 8 0 006 18z" fill="#1e293b" stroke="#38bdf8" strokeWidth="1.5"/><path d="M20 24h8M24 20v8" stroke="#38bdf8" strokeWidth="1.5" strokeLinecap="round"/></svg>);
    case 'hub':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><rect x="6" y="18" width="36" height="12" rx="2" fill="#1e293b" stroke="#94a3b8" strokeWidth="1.5"/><circle cx="14" cy="24" r="1.5" fill="#22c55e"/><circle cx="20" cy="24" r="1.5" fill="#22c55e"/><circle cx="26" cy="24" r="1.5" fill="#22c55e"/><circle cx="32" cy="24" r="1.5" fill="#22c55e"/><rect x="14" y="32" width="20" height="4" rx="1" fill="#1e293b"/></svg>);
    case 'laptop':
      return (<svg className={baseClass} viewBox="0 0 48 48" fill="none"><rect x="12" y="10" width="24" height="16" rx="1" fill="#1e293b" stroke="#64748b" strokeWidth="1.5"/><rect x="14" y="12" width="20" height="12" fill="#0ea5e9" opacity="0.2"/><path d="M8 32h32l-4-6H12l-4 6z" fill="#334155" stroke="#64748b" strokeWidth="1.5"/></svg>);
    default:
      return <svg className={baseClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="12" cy="12" r="10" /></svg>;
  }
}
