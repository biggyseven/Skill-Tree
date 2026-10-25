import { BaseEdge, EdgeLabelRenderer, getBezierPath } from '@xyflow/react';

export function CableEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}) {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const stroke = selected
    ? 'var(--emerald-300)'
    : data?.state === 'down'
      ? 'var(--rose-400)'
      : 'var(--cyan-400)';
  const strokeWidth = selected ? 4 : 3;
  const strokeDasharray = data?.state === 'down' && !selected ? '4 4' : undefined;

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{ stroke, strokeWidth, strokeDasharray, fill: 'none' }}
        interactionWidth={18}
      />
      {data?.label && (
        <EdgeLabelRenderer>
          <div
            className="pointer-events-none absolute rounded border border-[var(--s2)] bg-[var(--s1)] px-2 py-0.5 font-mono text-[10px] text-[var(--text-primary)] shadow-sm"
            style={{ transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)` }}
            title={data.cable_type || 'CÃ¢ble rÃ©seau'}
          >
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}
