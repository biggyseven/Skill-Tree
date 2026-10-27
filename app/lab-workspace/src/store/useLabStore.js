import { create } from 'zustand';

function normalisePortHandleId(handleId) {
  return String(handleId ?? '').replace(/::(?:source|target)$/, '');
}

const emptyTopology = () => ({
  schema_version: 2, topology_id: 'workspace-' + Date.now(),
  metadata: { name: 'Espace de travail libre', author: 'user', created_at: new Date().toISOString(), mode: 'lab' },
  nodes: [], links: [], simulation: { state: 'idle', event_log: [] },
});

const demoTopology = () => ({
  schema_version: 2, topology_id: 'demo',
  metadata: { name: 'Demo', author: 'demo', created_at: new Date().toISOString(), mode: 'lab' },
  nodes: [
    { id: 'R1', type: 'router', model: 'generic', x: 100, y: 200, label: 'R1', hostname: 'R1',
      ports: [
        { id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.0.12.1', mask: '255.255.255.252' },
        { id: 'Fa0/1', name: 'Fa0/1', state: 'down', ip: null, mask: null },
      ], config: { hostname: 'R1' } },
    { id: 'R2', type: 'router', model: 'generic', x: 450, y: 200, label: 'R2', hostname: 'R2',
      ports: [
        { id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.0.12.2', mask: '255.255.255.252' },
        { id: 'Fa0/1', name: 'Fa0/1', state: 'up', ip: '10.0.23.1', mask: '255.255.255.252' },
      ], config: { hostname: 'R2' } },
  ],
  links: [
    { id: 'L1', from: { node: 'R1', port: 'Fa0/0' }, to: { node: 'R2', port: 'Fa0/0' }, cable_type: 'copper_straight', state: 'up' },
  ],
  simulation: { state: 'idle', event_log: [] },
});

export const useLabStore = create((set, get) => ({
  lab: null, topology: null, selectedDevice: null, checkResult: null, loading: false, error: null,
  activePacket: null,
  activeTool: 'select',

  setTool(tool) { set({ activeTool: tool }); },
  loadLab(labId, definition, initialTopology) {
    set({ lab: { ...(definition || {}), id: labId }, topology: initialTopology || emptyTopology(), loading: false, error: null, selectedDevice: null, checkResult: null, activePacket: null, activeTool: 'select' });
  },
  loadFreeWorkspace() {
    set({
      lab: {
        id: 'workspace-libre',
        title: 'Espace de travail libre',
        level: 'Libre',
        module: 'Atelier libre',
        prompt: 'Construisez votre propre topologie réseau. Ajoutez des équipements, reliez leurs interfaces et explorez leur configuration sans être noté sur un scénario de cours.',
        objectives: [
          'Ajouter les équipements nécessaires à votre réseau',
          'Relier les ports compatibles avec des câbles',
          'Sélectionner chaque équipement pour examiner et modifier sa configuration',
        ],
        hints: [],
        xp_reward: 0,
        badges: [],
        sandbox: true,
      },
      topology: emptyTopology(), loading: false, error: null,
      selectedDevice: null, checkResult: null, activePacket: null, activeTool: 'select',
    });
  },
  loadDemo() {
    set({ lab: { id: 'demo', title: 'Démo', level: 'debutant', prompt: 'Gérez le matériel depuis l’inspecteur.', objectives: [] }, topology: demoTopology(), loading: false, error: null, selectedDevice: null, checkResult: null, activePacket: null, activeTool: 'select' });
  },
  setError(err) { set({ error: String((err && err.message) || err), loading: false }); },
  setLoading(v) { set({ loading: !!v }); },
  setActivePacket(packet) { set({ activePacket: packet }); },
  
  updateNodePosition(nodeId, x, y) {
    const topo = get().topology; if (!topo) return;
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, x, y } : n) } });
  },
  
  addNode(type, x, y) {
    const prefix = type.charAt(0).toUpperCase() + type.slice(1);
    const existing = new Set((get().topology?.nodes || []).map(n => n.id));
    let id;
    do { id = prefix + '-' + crypto.randomUUID().slice(0, 8); } while (existing.has(id));
    let defaultPorts = [];
    if (type === 'router') defaultPorts = [{ id: 'Fa0/0', name: 'Fa0/0', state: 'down' }, { id: 'Fa0/1', name: 'Fa0/1', state: 'down' }];
    else if (type === 'switch') defaultPorts = Array.from({ length: 8 }).map((_, i) => ({ id: `Fa0/${i+1}`, name: `Fa0/${i+1}`, state: 'down' }));
    else defaultPorts = [{ id: 'eth0', name: 'eth0', state: 'down' }];

    const newNode = { id, type, x, y, label: id, ports: defaultPorts, config: { hostname: id } };
    set(s => ({ topology: { ...s.topology, nodes: [...s.topology.nodes, newNode] }, checkResult: null }));
  },

  // --- GESTION DU MATERIEL (HARDWARE) ---
  
  addPort(nodeId) {
    const topo = get().topology;
    if (!topo) return;
    const node = topo.nodes.find(n => n.id === nodeId);
    if (!node) return;
    const ports = node.ports || [];
    const prefix = ['router', 'switch'].includes(node.type) ? 'Fa0/' : 'eth';
    const used = new Set(ports.map(p => p.id || p.name));
    const indexes = ports
      .map(p => String(p.id || p.name || ''))
      .filter(name => name.startsWith(prefix))
      .map(name => Number.parseInt(name.slice(prefix.length), 10))
      .filter(Number.isFinite);
    let index = indexes.length ? Math.max(...indexes) + 1 : 0;
    let name = `${prefix}${index}`;
    while (used.has(name)) { index += 1; name = `${prefix}${index}`; }
    const newPort = { id: name, name, state: 'down', ip: null, mask: null };
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, ports: [...(n.ports || []), newPort] } : n) }, checkResult: null });
  },

  removePort(nodeId, portId) {
    const topo = get().topology;
    if (!topo) return;
    const node = topo.nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    // On ne peut pas supprimer un port s'il est connecté
    const isConnected = topo.links.some(l => 
      (l.from.node === nodeId && l.from.port === portId) || 
      (l.to.node === nodeId && l.to.port === portId)
    );
    if (isConnected) {
      alert("Impossible de supprimer ce port : un câble y est connecté.");
      return;
    }

    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, ports: n.ports.filter(p => p.id !== portId) } : n) }, checkResult: null });
  },

  togglePortState(nodeId, portId) {
    const topo = get().topology;
    if (!topo) return;
    const node = topo.nodes.find(n => n.id === nodeId);
    if (!node) return;
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, ports: n.ports.map(p => p.id === portId ? { ...p, state: p.state === 'up' ? 'down' : 'up' } : p) } : n) }, checkResult: null });
  },

  updatePortAddress(nodeId, portId, ip, mask) {
    const topo = get().topology;
    if (!topo) return;
    const node = topo.nodes.find(n => n.id === nodeId);
    if (!node || !(node.ports || []).some(port => port.id === portId)) return;
    const cleanIp = String(ip ?? '').trim();
    const cleanMask = String(mask ?? '').trim();
    set({
      topology: {
        ...topo,
        nodes: topo.nodes.map(n => n.id === nodeId
          ? { ...n, ports: n.ports.map(port => port.id === portId
            ? { ...port, ip: cleanIp || null, mask: cleanMask || null }
            : port) }
          : n),
      },
      checkResult: null,
    });
  },

  addLink(connection, type) {
    const topo = get().topology;
    if (!topo || !connection.source || !connection.target || connection.source === connection.target) return;
    const source = topo.nodes.find(n => n.id === connection.source);
    const target = topo.nodes.find(n => n.id === connection.target);
    const sourcePortId = normalisePortHandleId(connection.sourceHandle);
    const targetPortId = normalisePortHandleId(connection.targetHandle);
    const sourcePort = (source?.ports || []).some(p => p.id === sourcePortId);
    const targetPort = (target?.ports || []).some(p => p.id === targetPortId);
    if (!sourcePort || !targetPort) return;
    const newLink = {
      id: 'link-' + crypto.randomUUID(),
      from: { node: connection.source, port: sourcePortId },
      to: { node: connection.target, port: targetPortId },
      cable_type: ({
        cable_straight: 'copper_straight',
        cable_cross: 'copper_crossover',
        fiber: 'fiber',
        console: 'console',
        wireless: 'wireless',
      })[type] || 'copper_straight',
      state: 'up'
    };
    set({ topology: { ...topo, links: [...topo.links, newLink] }, activeTool: 'select', checkResult: null });
  },

  selectDevice(nodeId) { set({ selectedDevice: nodeId }); },
  setCheckResult(r) { set({ checkResult: r }); },
  clearCheckResult() { set({ checkResult: null }); },
}));

