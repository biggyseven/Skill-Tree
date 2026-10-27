import { EdgeLabelRenderer, getBezierPath } from '@xyflow/react';

export function CableEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data, selected }) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition,
  });

  let strokeColor = '#0ea5e9'; // Bleu
  let strokeDasharray = 'none';

  if (data?.cable_type === 'copper_crossover') { strokeColor = '#f97316'; strokeDasharray = '6,4'; } // Orange
  if (data?.cable_type === 'fiber') { strokeColor = '#a855f7'; } // Violet
  if (data?.cable_type === 'console') { strokeColor = '#eab308'; strokeDasharray = '3,3'; }
  if (data?.cable_type === 'wireless') { strokeColor = '#22c55e'; strokeDasharray = '2,5'; }
  if (data?.state === 'down') { strokeColor = '#ef4444'; strokeDasharray = '4,4'; } // Rouge
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
