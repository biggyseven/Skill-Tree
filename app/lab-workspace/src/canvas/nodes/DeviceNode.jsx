import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { DeviceIcon } from './DeviceIcon.jsx';

export function DeviceNode({ data, selected }) {
  const isUp = data.state === 'up';
  const ports = data.ports || [];
  
  const half = Math.ceil(ports.length / 2);
  const leftPorts = ports.slice(0, half);
  const rightPorts = ports.slice(half);

  // Chaque interface physique expose une poignée source et une poignée cible.
  // Les deux partagent l'identifiant du port : les connexions et leur rendu gardent
  // ainsi la même interface physique, qu'elle soit utilisée comme origine ou destination.
  const renderPorts = (portsList, position) => {
    if (portsList.length === 0) return null;
    return portsList.map((port, index) => {
      const topPercent = portsList.length === 1 ? 50 : 20 + (index * (60 / (portsList.length - 1)));
      const horizontalOffset = { [position === Position.Left ? 'left' : 'right']: '-6px' };
      return (
        <React.Fragment key={port.id}>
          <Handle
            type="source"
            position={position}
            id={port.id}
            aria-label={`Port ${port.id}, origine`}
            title={`${port.name || port.id} — origine du câble`}
            className="!h-2 !w-2 !bg-[#0ea5e9] !border-2 !border-[#7dd3fc] hover:!scale-150 transition-all rounded-sm"
            style={{ ...horizontalOffset, top: `calc(${topPercent}% - 4px)` }}
          />
          <Handle
            type="target"
            position={position}
            id={port.id}
            aria-label={`Port ${port.id}, destination`}
            title={`${port.name || port.id} — destination du câble`}
            className="!h-2 !w-2 !bg-[#334155] !border-2 !border-[#94a3b8] hover:!border-[#0ea5e9] hover:!bg-[#0ea5e9] hover:!scale-150 transition-all rounded-sm"
            style={{ ...horizontalOffset, top: `calc(${topPercent}% + 4px)` }}
          />
        </React.Fragment>
      );
    });
  };

  return (
    <div className={`relative flex flex-col items-center justify-center p-2 transition-all ${selected ? 'rounded-xl bg-[#0ea5e9]/10 outline outline-2 outline-[#0ea5e9] outline-offset-4' : ''}`}>
      
      <div className="relative flex h-16 w-16 items-center justify-center drop-shadow-xl">
        <DeviceIcon type={data.type} />
        <div className={`absolute -bottom-1 -right-1 h-3.5 w-3.5 rounded-full border-2 border-[#0d1117] ${isUp ? 'bg-[#10b981]' : 'bg-[#ef4444]'}`} />
      </div>

      <div className="mt-3 text-center bg-[#0d1117]/80 px-2 py-0.5 rounded backdrop-blur-sm">
        <div className="font-mono text-[12px] font-bold text-white tracking-wide">{data.label}</div>
      </div>

      {renderPorts(leftPorts, Position.Left)}
      {renderPorts(rightPorts, Position.Right)}
    </div>
  );
}
