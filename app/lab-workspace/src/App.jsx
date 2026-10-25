import { useCallback, useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  ConnectionLineType,
  addEdge,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';

import { nodeTypes, edgeTypes } from './canvas/nodeTypes.js';

const initialNodes = [
  {
    id: 'router-1',
    type: 'router',
    position: { x: 70, y: 110 },
    data: {
      label: 'R1',
      hostname: 'edge-router-01',
      model: 'ISR',
      state: 'up',
    },
  },
  {
    id: 'switch-1',
    type: 'switch',
    position: { x: 365, y: 105 },
    data: {
      label: 'SW1',
      hostname: 'access-sw-01',
      model: 'Catalyst',
      state: 'up',
    },
  },
  {
    id: 'pc-1',
    type: 'pc',
    position: { x: 690, y: 25 },
    data: {
      label: 'PC-01',
      hostname: 'poste-client-01',
      state: 'up',
    },
  },
  {
    id: 'firewall-1',
    type: 'firewall',
    position: { x: 365, y: 300 },
    data: {
      label: 'FW1',
      hostname: 'perimeter-fw',
      model: 'NGFW',
      state: 'down',
    },
  },
  {
    id: 'server-1',
    type: 'server',
    position: { x: 690, y: 300 },
    data: {
      label: 'SRV-01',
      hostname: 'app-server-01',
      model: 'Linux',
      state: 'up',
    },
  },
  {
    id: 'cloud-1',
    type: 'cloud',
    position: { x: 70, y: 360 },
    data: {
      label: 'WAN',
      hostname: 'cloud-edge',
      state: 'up',
    },
  },
];

const initialEdges = [
  {
    id: 'e-router-switch',
    source: 'router-1',
    sourceHandle: 'right-upper-source',
    target: 'switch-1',
    targetHandle: 'left-upper-target',
    type: 'cable',
    data: {
      state: 'up',
      cable_type: 'Ethernet cuivre',
      label: 'Gi0/0 → Gi0/1',
    },
  },
  {
    id: 'e-switch-pc',
    source: 'switch-1',
    sourceHandle: 'right-upper-source',
    target: 'pc-1',
    targetHandle: 'left-upper-target',
    type: 'cable',
    data: {
      state: 'up',
      cable_type: 'Ethernet cuivre',
      label: 'Fa0/2 → eth0',
    },
  },
  {
    id: 'e-switch-fw',
    source: 'switch-1',
    sourceHandle: 'right-lower-source',
    target: 'firewall-1',
    targetHandle: 'left-upper-target',
    type: 'cable',
    data: {
      state: 'down',
      cable_type: 'Fibre optique',
      label: 'Gi0/2 → Port1',
    },
  },
  {
    id: 'e-fw-server',
    source: 'firewall-1',
    sourceHandle: 'right-lower-source',
    target: 'server-1',
    targetHandle: 'left-lower-target',
    type: 'cable',
    data: {
      state: 'up',
      cable_type: 'Ethernet cuivre',
      label: 'Port2 → eth0',
    },
  },
  {
    id: 'e-cloud-router',
    source: 'cloud-1',
    sourceHandle: 'right-upper-source',
    target: 'router-1',
    targetHandle: 'left-lower-target',
    type: 'cable',
    data: {
      state: 'up',
      cable_type: 'WAN',
      label: 'Internet → Gi0/1',
    },
  },
];

const defaultEdgeOptions = {
  type: 'cable',
};

export default function App() {
  const [theme, setTheme] = useState('dark');

  // États contrôlés : les déplacements et les changements de liens
  // sont enregistrés dans React.
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Création d'un nouveau câble lorsqu'un handle source est relié
  // à un handle cible.
  const onConnect = useCallback(
    (connection) => {
      setEdges((currentEdges) =>
        addEdge(
          {
            ...connection,
            type: 'cable',
            data: {
              state: 'up',
              cable_type: 'Ethernet cuivre',
              label: 'Ethernet cuivre',
            },
          },
          currentEdges,
        ),
      );
    },
    [setEdges],
  );

  return (
    <div className="theme-root min-h-screen" data-theme={theme}>
      <header className="flex min-h-[72px] flex-wrap items-center justify-between gap-4 border-b border-[var(--s2)] px-5 py-3">
        <div>
          <h1 className="text-lg font-bold text-[var(--text-primary)]">
            Skill Tree{' '}
            <span className="text-[var(--cyan-400)]">
              / Lab Workspace
            </span>
          </h1>

          <p className="text-xs text-zinc-500">
            M3 · SVG icons · nœuds personnalisés · câbles Bézier
          </p>
        </div>

        <button
          type="button"
          onClick={() =>
            setTheme((value) =>
              value === 'dark' ? 'light' : 'dark',
            )
          }
          className="rounded-lg border border-[var(--s2)] bg-[var(--s1)] px-3 py-2 text-sm text-[var(--text-primary)]"
        >
          Passer au thème {theme === 'dark' ? 'clair' : 'sombre'}
        </button>
      </header>

      <div className="h-[calc(100vh-72px)] min-h-[500px] w-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          defaultEdgeOptions={defaultEdgeOptions}
          connectionLineType={ConnectionLineType.Bezier}
          nodesDraggable={true}
          nodesConnectable={true}
          elementsSelectable={true}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          colorMode={theme}
        >
          <Background
            variant={BackgroundVariant.Dots}
            color="var(--s2)"
            gap={18}
            size={1.2}
          />

          <Controls />
          <MiniMap pannable zoomable />
        </ReactFlow>
      </div>
    </div>
  );
}
