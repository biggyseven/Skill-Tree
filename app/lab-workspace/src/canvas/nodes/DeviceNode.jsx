import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { DeviceIcon } from './DeviceIcon.jsx';

export function DeviceNode({ data, selected }) {
  const isUp = data.state === 'up';
  const ports = data.ports || [];
  
  const half = Math.ceil(ports.length / 2);
  const leftPorts = ports.slice(0, half);
  const rightPorts = ports.slice(half);

  const renderPorts = (portsList, position, type) => {
    if (portsList.length === 0) return null;
    return portsList.map((port, index) => {
      // Calcul de l'espacement (20% à 80%) pour ne pas chevaucher le haut/bas
      const topPercent = portsList.length === 1 
        ? 50 
        : 20 + (index * (60 / (portsList.length - 1)));
      
      return (
        <Handle 
          key={port.id}
          type={type} 
          position={position} 
          id={port.id} 
          className="!h-3 !w-3 !bg-[#1e293b] !border-2 !border-[#64748b] hover:!border-[#0ea5e9] hover:!bg-[#0ea5e9] transition-colors rounded-sm"
          style={{ 
            [position === Position.Left ? 'left' : 'right']: '-6px', 
            top: `${topPercent}%` 
          }} 
        />
      );
    });
  };

  return (
    <div className={`relative flex flex-col items-center justify-center p-2 transition-colors ${selected ? 'rounded-lg bg-[#0ea5e9]/10 outline outline-1 outline-[#0ea5e9]' : ''}`}>
      
      <div className="relative flex h-14 w-14 items-center justify-center rounded bg-[#0f172a] border border-[#334155] shadow-lg">
        <DeviceIcon type={data.type} />
        <div className={`absolute -bottom-1 -right-1 h-3 w-3 rounded-full border-2 border-[#0f172a] ${isUp ? 'bg-[#10b981]' : 'bg-[#f43f5e]'}`} />
      </div>

      <div className="mt-2 text-center">
        <div className="font-mono text-[12px] font-bold text-[#e2e8f0]">{data.label}</div>
      </div>

      {renderPorts(leftPorts, Position.Left, 'target')}
      {renderPorts(rightPorts, Position.Right, 'source')}
    </div>
  );
}
