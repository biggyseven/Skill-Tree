import { useEffect, useRef } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import { CLIParser } from './parser.js';
import { useLabStore } from '../store/useLabStore.js';

export function CLITab() {
  const selectedDeviceId = useLabStore(s => s.selectedDevice);
  const topology = useLabStore(s => s.topology);
  const termRef = useRef(null);
  const parserRef = useRef(null);
  const termInstanceRef = useRef(null);

  const device = topology?.nodes.find(n => n.id === selectedDeviceId);

  useEffect(() => {
    if (!device || !termRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: { background: '#0c0a1a', foreground: '#e2e8f0', cursor: '#0dbedc', selectionBackground: 'rgba(52, 211, 153, 0.3)' },
      fontFamily: '"JetBrains Mono", monospace', fontSize: 13, convertEol: true, scrollback: 1000,
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(termRef.current);
    fit.fit();
    termInstanceRef.current = term;

    parserRef.current = new CLIParser(device);
    
    let currentLine = '';
    const prompt = () => `\r\n\x1b[32m${parserRef.current.getPrompt()}\x1b[0m `;
    term.write(`Cisco IOS Software, SkillTree Edition\r\nPress RETURN to get started.\r\n`);
    term.write(prompt());

    term.onData(data => {
      const code = data.charCodeAt(0);
      if (code === 13) { // Enter
        term.write('\r\n');
        if (currentLine.trim()) {
          const topologyBefore = JSON.stringify(useLabStore.getState().topology);
          const res = parserRef.current.execute(currentLine);
          if (res.output) term.write(res.output.replace(/\n/g, '\r\n') + '\r\n');
          const topologyChanged = topologyBefore !== JSON.stringify(useLabStore.getState().topology);
          useLabStore.setState(s => ({ topology: { ...s.topology }, ...(topologyChanged ? { checkResult: null } : {}) }));
          
          // Si c'est asynchrone (ex: ping), on n'affiche pas le prompt tout de suite
          if (!res.isAsync) {
            term.write(prompt());
          }
        } else {
          term.write(prompt());
        }
        currentLine = '';
      } else if (code === 127) { // Backspace
        if (currentLine.length > 0) {
          currentLine = currentLine.slice(0, -1);
          term.write('\b \b');
        }
      } else if (code >= 32 && code <= 126) { // Caractères imprimables
        currentLine += data;
        term.write(data);
      }
    });

    // ÉCOUTEUR POUR LE RÉSULTAT DU PING
    const handlePingResult = (e) => {
      const res = e.detail.result;
      const output = res.success 
        ? `!!!!!\nSuccess rate is 100 percent (5/5), round-trip min/avg/max = 1/1/1 ms`
        : `.....\nSuccess rate is 0 percent (0/5)`;
      term.write(`\r\n${output}\r\n`);
      term.write(prompt()); 
    };
    window.addEventListener('cli:ping-result', handlePingResult);

    return () => { 
      term.dispose(); 
      window.removeEventListener('cli:ping-result', handlePingResult);
    };
  }, [device?.id]);

  if (!selectedDeviceId) {
    return <div className="flex h-full items-center justify-center p-6 text-center text-xs text-[var(--text-muted)]">Sélectionnez un équipement sur le canevas<br/>pour ouvrir sa console CLI.</div>;
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex shrink-0 items-center justify-between border-b border-[var(--s2)] bg-[var(--s1)] px-4 py-2 text-xs">
        <span className="font-bold text-[var(--text-primary)]">CLI — {device?.config?.hostname || device?.id}</span>
      </div>
      <div className="flex-1 overflow-hidden bg-[#0c0a1a] p-2" ref={termRef} />
    </div>
  );
}
