import { useCallback, useMemo } from 'react';
import { ReactFlow, Background, BackgroundVariant, Controls, MiniMap } from '@xyflow/react';
import { useLabStore } from '../store/useLabStore.js';
import { nodeTypes, edgeTypes } from './nodeTypes.js';

const defaultEdgeOptions = { type: 'cable' };

export function LabCanvas() {
  const topology = useLabStore(s => s.topology);
  const selectDevice = useLabStore(s => s.selectDevice);
  const updateNodePosition = useLabStore(s => s.updateNodePosition);

  const flowNodes = useMemo(() => {
    if (!topology) return [];
    return topology.nodes.map(n => {
      const anyUp = (n.ports || []).some(p => p.state === 'up');
      return {
        id: n.id, type: n.type, position: { x: n.x || 100, y: n.y || 100 },
        data: { label: n.label || n.id, hostname: (n.config && n.config.hostname) || n.id, model: n.model || '', state: anyUp ? 'up' : 'down' },
      };
    });
  }, [topology]);

  const flowEdges = useMemo(() => {
    if (!topology) return [];
    return topology.links.map(l => ({
      id: l.id, source: l.from.node, target: l.to.node, type: 'cable',
      data: { state: l.state, cable_type: l.cable_type, label: l.from.port + ' → ' + l.to.port },
    }));
  }, [topology]);

  const onNodesChange = useCallback((changes) => {
    changes.forEach(c => { if (c.type === 'position' && c.position) updateNodePosition(c.id, c.position.x, c.position.y); });
  }, [updateNodePosition]);

  const onNodeClick = useCallback((_e, node) => selectDevice(node.id), [selectDevice]);

  if (!topology) return null;

  return (
    <div className="flex-1 min-h-0">
      <ReactFlow nodes={flowNodes} edges={flowEdges} onNodesChange={onNodesChange} onNodeClick={onNodeClick}
        nodeTypes={nodeTypes} edgeTypes={edgeTypes} defaultEdgeOptions={defaultEdgeOptions}
        fitView fitViewOptions={{ padding: 0.2 }} proOptions={{ hideAttribution: true }}>
        <Background variant={BackgroundVariant.Dots} color="var(--s2)" gap={18} size={1.2} />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
