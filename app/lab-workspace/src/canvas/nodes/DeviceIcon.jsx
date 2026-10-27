import React from 'react';

export function DeviceIcon({ type, className }) {
  const baseClass = className || "w-12 h-12";
  
  switch (type) {
    case 'router':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <circle cx="24" cy="24" r="20" fill="#1e3a8a" stroke="#3b82f6" strokeWidth="2"/>
          <path d="M12 24h8m8 0h8M20 24l4-4m-4 4l4 4m4-4l-4-4m4 4l-4 4" stroke="#60a5fa" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="24" cy="24" r="4" fill="#1e3a8a" stroke="#3b82f6" strokeWidth="2"/>
          <circle cx="38" cy="16" r="2" fill="#10b981"/>
          <circle cx="38" cy="32" r="2" fill="#ef4444"/>
        </svg>
      );
    case 'switch':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="6" y="14" width="36" height="20" rx="2" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <path d="M10 20h2m2 0h2m2 0h2m2 0h2m2 0h2m2 0h2" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round"/>
          <path d="M10 24h2m2 0h2m2 0h2m2 0h2m2 0h2m2 0h2" stroke="#eab308" strokeWidth="2.5" strokeLinecap="round"/>
          <rect x="14" y="30" width="20" height="4" rx="1" fill="#1e293b"/>
        </svg>
      );
    case 'pc':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="10" y="8" width="28" height="20" rx="2" fill="#1e293b" stroke="#64748b" strokeWidth="2"/>
          <rect x="12" y="10" width="24" height="16" fill="#0ea5e9" opacity="0.3"/>
          <path d="M22 28v6m-6 0h12m-14 4h16" stroke="#64748b" strokeWidth="2.5" strokeLinecap="round"/>
          <rect x="16" y="34" width="16" height="6" rx="1" fill="#334155"/>
        </svg>
      );
    case 'server':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="12" y="6" width="24" height="36" rx="2" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <rect x="16" y="10" width="16" height="8" rx="1" fill="#1e293b" stroke="#475569"/>
          <rect x="16" y="20" width="16" height="8" rx="1" fill="#1e293b" stroke="#475569"/>
          <rect x="16" y="30" width="16" height="8" rx="1" fill="#1e293b" stroke="#475569"/>
          <circle cx="20" cy="14" r="1.5" fill="#10b981"/>
          <circle cx="20" cy="24" r="1.5" fill="#eab308"/>
          <circle cx="20" cy="34" r="1.5" fill="#3b82f6"/>
        </svg>
      );
    case 'firewall':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="8" y="10" width="32" height="28" rx="2" fill="#450a0a" stroke="#ef4444" strokeWidth="2"/>
          <path d="M8 18h32M8 26h32M8 34h32M20 10v8M28 18v8M20 26v8" stroke="#ef4444" strokeWidth="2"/>
          <path d="M24 22l4 4m0-4l-4 4" stroke="#fca5a5" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
      );
    case 'cloud':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <path d="M16 34h16a8 8 0 000-16 12 12 0 00-22-2 8 8 0 006 18z" fill="#1e293b" stroke="#38bdf8" strokeWidth="2"/>
          <path d="M20 24h8M24 20v8" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
      );
    case 'hub':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="6" y="16" width="36" height="16" rx="2" fill="#1e293b" stroke="#94a3b8" strokeWidth="2"/>
          <circle cx="14" cy="24" r="2" fill="#10b981"/>
          <circle cx="20" cy="24" r="2" fill="#10b981"/>
          <circle cx="26" cy="24" r="2" fill="#10b981"/>
          <circle cx="32" cy="24" r="2" fill="#10b981"/>
        </svg>
      );
    case 'laptop':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="12" y="10" width="24" height="16" rx="1" fill="#1e293b" stroke="#64748b" strokeWidth="2"/>
          <rect x="14" y="12" width="20" height="12" fill="#0ea5e9" opacity="0.3"/>
          <path d="M8 34h32l-4-8H12l-4 8z" fill="#334155" stroke="#64748b" strokeWidth="2"/>
        </svg>
      );
    case 'printer':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <path d="M14 18V7h20v11M14 34H9a4 4 0 0 1-4-4v-8a4 4 0 0 1 4-4h30a4 4 0 0 1 4 4v8a4 4 0 0 1-4 4h-5" stroke="#64748b" strokeWidth="2.5" strokeLinejoin="round"/>
          <rect x="14" y="27" width="20" height="14" rx="2" fill="#1e293b" stroke="#38bdf8" strokeWidth="2"/>
          <circle cx="37" cy="22" r="2" fill="#10b981"/>
          <path d="M18 32h12m-12 4h9" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      );
    case 'phone':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="7" y="5" width="34" height="38" rx="5" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <rect x="12" y="10" width="24" height="9" rx="2" fill="#0e7490" stroke="#38bdf8" strokeWidth="1.5"/>
          <path d="M14 25h20m-18 4h16m-14 4h12" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="24" cy="38" r="1.5" fill="#10b981"/>
        </svg>
      );
    case 'database':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <ellipse cx="24" cy="11" rx="15" ry="6" fill="#1e3a8a" stroke="#60a5fa" strokeWidth="2"/>
          <path d="M9 11v26c0 3.3 6.7 6 15 6s15-2.7 15-6V11M9 20c0 3.3 6.7 6 15 6s15-2.7 15-6M9 29c0 3.3 6.7 6 15 6s15-2.7 15-6" stroke="#60a5fa" strokeWidth="2"/>
          <circle cx="33" cy="15" r="1.5" fill="#10b981"/>
        </svg>
      );
    case 'storage':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="6" y="8" width="36" height="32" rx="3" fill="#172554" stroke="#818cf8" strokeWidth="2"/>
          <rect x="11" y="13" width="26" height="8" rx="1.5" fill="#1e293b" stroke="#6366f1"/>
          <rect x="11" y="25" width="26" height="8" rx="1.5" fill="#1e293b" stroke="#6366f1"/>
          <circle cx="16" cy="17" r="1.5" fill="#10b981"/><circle cx="16" cy="29" r="1.5" fill="#10b981"/>
          <path d="M22 17h10m-10 12h10" stroke="#a5b4fc" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      );
    case 'load_balancer':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="15" y="5" width="18" height="10" rx="2" fill="#0f172a" stroke="#38bdf8" strokeWidth="2"/>
          <rect x="4" y="33" width="12" height="10" rx="2" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <rect x="18" y="33" width="12" height="10" rx="2" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <rect x="32" y="33" width="12" height="10" rx="2" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <path d="M24 15v7M10 33v-6h28v6M24 22l-14 5m14-5l14 5" stroke="#38bdf8" strokeWidth="2" strokeLinejoin="round"/>
        </svg>
      );
    case 'wireless_controller':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="6" y="20" width="36" height="17" rx="3" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <circle cx="14" cy="28" r="2" fill="#10b981"/><circle cx="21" cy="28" r="2" fill="#eab308"/>
          <path d="M24 14c4-4 10-4 14 0M28 18c2-2 5-2 7 0M13 14c4-4 10-4 14 0M17 18c2-2 5-2 7 0" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      );
    case 'access_point':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="7" y="29" width="34" height="10" rx="3" fill="#0f172a" stroke="#38bdf8" strokeWidth="2"/>
          <circle cx="16" cy="34" r="1.5" fill="#10b981"/><circle cx="22" cy="34" r="1.5" fill="#10b981"/>
          <path d="M12 22a17 17 0 0 1 24 0M17 26a10 10 0 0 1 14 0M22 30a3 3 0 0 1 4 0" stroke="#38bdf8" strokeWidth="2.5" strokeLinecap="round"/>
        </svg>
      );
    case 'modem':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <rect x="5" y="17" width="38" height="21" rx="3" fill="#0f172a" stroke="#64748b" strokeWidth="2"/>
          <path d="M12 17V8m24 9V8" stroke="#64748b" strokeWidth="2.5" strokeLinecap="round"/>
          <circle cx="13" cy="29" r="2" fill="#10b981"/><circle cx="21" cy="29" r="2" fill="#eab308"/>
          <path d="M28 28h9m-9 4h9" stroke="#38bdf8" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      );
    case 'vpn_gateway':
      return (
        <svg className={baseClass} viewBox="0 0 48 48" fill="none">
          <path d="M24 4l16 6v12c0 10-7 17-16 22C15 39 8 32 8 22V10l16-6z" fill="#450a0a" stroke="#ef4444" strokeWidth="2"/>
          <rect x="15" y="20" width="18" height="14" rx="2" fill="#1e293b" stroke="#fca5a5" strokeWidth="2"/>
          <path d="M19 20v-3a5 5 0 0 1 10 0v3m-5 5v4" stroke="#fca5a5" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      );
    default:
      return <svg className={baseClass} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /></svg>;
  }
}
