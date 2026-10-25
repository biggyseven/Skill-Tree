import { create } from 'zustand';

const emptyTopology = () => ({
  schema_version: 2, topology_id: 'demo-' + Date.now(),
  metadata: { name: 'Sans titre', author: 'user', created_at: new Date().toISOString(), mode: 'lab' },
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
    set({ lab: { id: labId, ...(definition || {}) }, topology: initialTopology || emptyTopology(), loading: false, error: null, selectedDevice: null, checkResult: null, activePacket: null });
  },
  loadDemo() {
    set({ lab: { id: 'demo', title: 'Démo', level: 'debutant', prompt: 'Gérez le matériel depuis l’inspecteur.', objectives: [] }, topology: demoTopology(), loading: false, error: null });
  },
  setError(err) { set({ error: String((err && err.message) || err), loading: false }); },
  setLoading(v) { set({ loading: !!v }); },
  setActivePacket(packet) { set({ activePacket: packet }); },
  
  updateNodePosition(nodeId, x, y) {
    const topo = get().topology; if (!topo) return;
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, x, y } : n) } });
  },
  
  addNode(type, x, y) {
    const id = type.charAt(0).toUpperCase() + type.slice(1) + '-' + Math.floor(Math.random() * 1000);
    let defaultPorts = [];
    if (type === 'router') defaultPorts = [{ id: 'Fa0/0', name: 'Fa0/0', state: 'down' }, { id: 'Fa0/1', name: 'Fa0/1', state: 'down' }];
    else if (type === 'switch') defaultPorts = Array.from({ length: 8 }).map((_, i) => ({ id: `Fa0/${i+1}`, name: `Fa0/${i+1}`, state: 'down' }));
    else defaultPorts = [{ id: 'eth0', name: 'eth0', state: 'down' }];

    const newNode = { id, type, x, y, label: id, ports: defaultPorts, config: { hostname: id } };
    set(s => ({ topology: { ...s.topology, nodes: [...s.topology.nodes, newNode] } }));
  },

  // --- GESTION DU MATERIEL (HARDWARE) ---
  
  addPort(nodeId) {
    const topo = get().topology;
    const node = topo.nodes.find(n => n.id === nodeId);
    if (!node) return;
    const currentCount = node.ports?.length || 0;
    const newPort = { id: `Fa0/${currentCount}`, name: `Fa0/${currentCount}`, state: 'down', ip: null, mask: null };
    
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, ports: [...(n.ports || []), newPort] } : n) } });
  },

  removePort(nodeId, portId) {
    const topo = get().topology;
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

    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, ports: n.ports.filter(p => p.id !== portId) } : n) } });
  },

  togglePortState(nodeId, portId) {
    const topo = get().topology;
    const node = topo.nodes.find(n => n.id === nodeId);
    if (!node) return;
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, ports: n.ports.map(p => p.id === portId ? { ...p, state: p.state === 'up' ? 'down' : 'up' } : p) } : n) } });
  },

  addLink(connection, type) {
    const topo = get().topology;
    const newLink = {
      id: 'link-' + Date.now(),
      from: { node: connection.source, port: connection.sourceHandle },
      to: { node: connection.target, port: connection.targetHandle },
      cable_type: type === 'cable_cross' ? 'copper_cross' : (type === 'fiber' ? 'fiber' : 'copper_straight'),
      state: 'up'
    };
    set({ topology: { ...topo, links: [...topo.links, newLink] }, activeTool: 'select' });
  },

  selectDevice(nodeId) { set({ selectedDevice: nodeId }); },
  setCheckResult(r) { set({ checkResult: r }); },
  clearCheckResult() { set({ checkResult: null }); },
}));

