import { EdgeLabelRenderer, getBezierPath } from '@xyflow/react';

export function CableEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data, selected }) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition,
  });

  let strokeColor = '#0ea5e9'; // Cuivre droit
  let strokeDasharray = 'none';
  const cableType = data?.cable_type;

  if (cableType === 'copper_crossover' || cableType === 'serial_dce') {
    strokeColor = '#f97316'; strokeDasharray = '6,4';
  }
  if (cableType === 'fiber' || cableType === 'fiber_multimode') strokeColor = '#a855f7';
  if (cableType === 'fiber_singlemode') { strokeColor = '#ec4899'; strokeDasharray = '7,3'; }
  if (cableType === 'console') { strokeColor = '#eab308'; strokeDasharray = '3,3'; }
  if (cableType === 'console_usb') { strokeColor = '#facc15'; strokeDasharray = '1,3'; }
  if (cableType === 'dac') { strokeColor = '#06b6d4'; strokeDasharray = '2,2'; }
  if (cableType === 'coaxial') { strokeColor = '#f59e0b'; strokeDasharray = '8,3'; }
  if (cableType === 'telephone') { strokeColor = '#94a3b8'; strokeDasharray = '2,3'; }
  if (cableType === 'ethernet_cat6a') { strokeColor = '#38bdf8'; strokeDasharray = 'none'; }
  if (cableType === 'ethernet_cat8') { strokeColor = '#0284c7'; strokeDasharray = '5,2'; }
  if (cableType === 'copper_poe') { strokeColor = '#84cc16'; strokeDasharray = '3,2'; }
  if (cableType === 'fiber_gpon') { strokeColor = '#8b5cf6'; strokeDasharray = '4,2'; }
  if (cableType === 'fiber_armored') { strokeColor = '#d946ef'; strokeDasharray = '9,3'; }
  if (cableType === 'fiber_lc_patch') { strokeColor = '#c084fc'; strokeDasharray = '1,2'; }
  if (cableType === 'console_usb_c') { strokeColor = '#fde047'; strokeDasharray = '1,2'; }
  if (cableType === 'serial_rs232') { strokeColor = '#fb7185'; strokeDasharray = '2,3'; }
  if (cableType === 'dac_qsfp') { strokeColor = '#14b8a6'; strokeDasharray = '2,2'; }
  if (cableType === 'wireless') { strokeColor = '#22c55e'; strokeDasharray = '2,5'; }
  if (data?.state === 'down') { strokeColor = '#ef4444'; strokeDasharray = '4,4'; }
  if (selected) { strokeColor = '#10b981'; }

  return (
    <>
      {/* Ombre du câble pour l'effet 3D */}
      <path
        d={edgePath}
        style={{
          stroke: 'rgba(0,0,0,0.6)',
          strokeWidth: 5,
          fill: 'none',
          transform: 'translate(2px, 2px)',
        }}
      />
      {/* Le câble */}
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        style={{
          stroke: strokeColor,
          strokeWidth: selected ? 4 : 3,
          strokeDasharray: strokeDasharray,
          fill: 'none',
          transition: 'stroke 0.2s'
        }}
      />
      {/* Étiquette */}
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            className="pointer-events-none absolute rounded border border-[#334155] bg-[#0d1117] px-2 py-0.5 font-mono text-[10px] font-bold text-[#cbd5e1] shadow-xl"
            style={{ transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)` }}
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
