const iconShapes = {
  router: <><rect x="3" y="7" width="18" height="10" rx="2" /><circle cx="8" cy="12" r="1.1" /><circle cx="16" cy="12" r="1.1" /><path d="M5.5 5h13M5.5 19h13" /></>,
  switch: <><rect x="2.5" y="6.5" width="19" height="11" rx="2" /><rect x="4.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="6.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="8.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="10.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="12.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="14.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="16.1" y="10" width="1.4" height="4" rx="0.2" /><rect x="18.1" y="10" width="1.4" height="4" rx="0.2" /></>,
  pc: <><rect x="3" y="3" width="18" height="13" rx="1.5" /><path d="M12 16v4m-4 1h8m-6-1h4" /></>,
  firewall: <><path d="M3 5.5h8v4H3zM13 5.5h8v4h-8zM7 10.5h8v4H7zM17 10.5h4v4h-4zM3 15.5h8v4H3zM13 15.5h8v4h-8z" /><path d="M11 5.5v4m2 1v4m-2 1v4" /></>,
  server: <><rect x="3" y="3" width="18" height="7" rx="1.5" /><rect x="3" y="14" width="18" height="7" rx="1.5" /><circle cx="7" cy="6.5" r="1" /><circle cx="7" cy="17.5" r="1" /><path d="M11 6.5h6m-6 11h6" /></>,
  cloud: <path d="M6.6 19h10.8a3.6 3.6 0 0 0 .6-7.15A5.8 5.8 0 0 0 6.5 10a4.5 4.5 0 0 0 .1 9Z" />,
};

export function DeviceIcon({ kind, className = '' }) {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      {iconShapes[kind] || iconShapes.router}
    </svg>
  );
}
