import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { DeviceIcon } from './DeviceIcon.jsx';

export function DeviceNode({ data, selected }) {
  const isUp = data.state === 'up';
  const ports = data.ports || [];
  
  const half = Math.ceil(ports.length / 2);
  const leftPorts = ports.slice(0, half);
  const rightPorts = ports.slice(half);

  // Chaque interface physique expose un point de départ et un point d'arrivée.
  // Les deux handles sont légèrement décalés pour rester faciles à sélectionner.
  const renderPorts = (portsList, position) => {
    if (portsList.length === 0) return null;
    return portsList.map((port, index) => {
      const topPercent = portsList.length === 1 ? 50 : 8 + (index * (84 / (portsList.length - 1)));
      const sideStyle = position === Position.Left ? { left: '-5px' } : { right: '-5px' };
      const name = port.name || port.id;
      return (
        <React.Fragment key={port.id}>
          <Handle
            type="source"
            position={position}
            id={`${port.id}::source`}
            title={`Port ${name} — départ du câble`}
            aria-label={`Port ${name}, départ du câble`}
            className="!h-2 !w-2 !bg-[#0ea5e9] !border !border-[#7dd3fc] hover:!bg-[#38bdf8] hover:!scale-125 transition-all rounded-sm"
            style={{ ...sideStyle, top: `calc(${topPercent}% - 4px)` }}
          />
          <Handle
            type="target"
            position={position}
            id={`${port.id}::target`}
            title={`Port ${name} — arrivée du câble`}
            aria-label={`Port ${name}, arrivée du câble`}
            className="!h-2 !w-2 !bg-[#64748b] !border !border-[#cbd5e1] hover:!bg-[#38bdf8] hover:!scale-125 transition-all rounded-sm"
            style={{ ...sideStyle, top: `calc(${topPercent}% + 4px)` }}
          />
        </React.Fragment>
      );
    });
  };

  const nodeMinHeight = ports.length > 16 ? `${Math.ceil(ports.length / 2) * 8 + 48}px` : undefined;

  return (
    <div style={nodeMinHeight ? { minHeight: nodeMinHeight } : undefined} className={`relative flex flex-col items-center justify-center p-2 transition-all ${selected ? 'rounded-xl bg-[#0ea5e9]/10 outline outline-2 outline-[#0ea5e9] outline-offset-4' : ''}`}>
      
      <div className="relative flex h-16 w-16 items-center justify-center drop-shadow-xl">
        <DeviceIcon type={data.iconType || data.type} />
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
