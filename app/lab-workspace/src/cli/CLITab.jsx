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

  const device = topology?.nodes.find(n => n.id === selectedDeviceId);

  useEffect(() => {
    if (!device || !termRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: { 
        background: '#0c0a1a', 
        foreground: '#e2e8f0',
        cursor: '#0dbedc',
        selectionBackground: 'rgba(52, 211, 153, 0.3)'
      },
      fontFamily: '"JetBrains Mono", monospace',
      fontSize: 13,
      convertEol: true,
      scrollback: 1000,
    });
    const fit = new FitAddon();
    term.loadAddon(fit);
    term.open(termRef.current);
    fit.fit();

    parserRef.current = new CLIParser(device);
    
    let currentLine = '';
    const prompt = () => `\r\n\x1b[32m${parserRef.current.getPrompt()}\x1b[0m `;
    term.write(`Cisco IOS Software, SkillTree Edition\r\nPress RETURN to get started.\r\n`);
    term.write(prompt());

    term.onData(data => {
      const code = data.charCodeAt(0);
      if (code === 13) {
        term.write('\r\n');
        if (currentLine.trim()) {
          const res = parserRef.current.execute(currentLine);
          if (res.output) term.write(res.output.replace(/\n/g, '\r\n') + '\r\n');
          // FORCER LA MISE A JOUR REACT FLOW
          useLabStore.setState(s => ({ topology: { ...s.topology } }));
        }
        currentLine = '';
        term.write(prompt());
      } else if (code === 127) {
        if (currentLine.length > 0) {
          currentLine = currentLine.slice(0, -1);
          term.write('\b \b');
        }
      } else if (code >= 32 && code <= 126) {
        currentLine += data;
        term.write(data);
      }
    });

    return () => { term.dispose(); };
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
