import { EdgeLabelRenderer, getBezierPath } from '@xyflow/react';

export function CableEdge({ id, sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, data, selected }) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition,
  });

  // Couleurs forcées en dur pour garantir la visibilité
  let strokeColor = '#0ea5e9'; // Bleu (Câble droit)
  let strokeDasharray = 'none';

  if (data?.cable_type === 'copper_cross') {
    strokeColor = '#fb923c'; // Orange (Câble croisé)
    strokeDasharray = '5,5';
  } else if (data?.cable_type === 'fiber') {
    strokeColor = '#c084fc'; // Violet (Fibre)
  }

  if (data?.state === 'down') {
    strokeColor = '#f43f5e'; // Rouge (Down)
    strokeDasharray = '4,4';
  }
  if (selected) {
    strokeColor = '#10b981'; // Vert émeraude si sélectionné
  }

  return (
    <>
      {/* Le chemin du câble */}
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
      {/* L'étiquette du câble */}
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            className="pointer-events-none absolute rounded border border-[#334155] bg-[#0f172a] px-2 py-0.5 font-mono text-[10px] font-bold text-white shadow-md"
            style={{ transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)` }}
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
