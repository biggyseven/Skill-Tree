import { create } from 'zustand';

const emptyTopology = () => ({
  schema_version: 2,
  topology_id: 'demo-' + Date.now(),
  metadata: { name: 'Sans titre', author: 'user', created_at: new Date().toISOString(), mode: 'lab' },
  nodes: [], links: [], simulation: { state: 'idle', event_log: [] },
});

const demoTopology = () => ({
  schema_version: 2,
  topology_id: 'demo',
  metadata: { name: 'Demo', author: 'demo', created_at: new Date().toISOString(), mode: 'lab' },
  nodes: [
    { id: 'R1', type: 'router', model: 'generic', x: 100, y: 200, label: 'R1', hostname: 'R1',
      ports: [
        { id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.0.12.1', mask: '255.255.255.252' },
        { id: 'Fa0/1', name: 'Fa0/1', state: 'down', ip: null, mask: null },
      ],
      config: { hostname: 'R1', vlans: [], routes: [], ospf: { enabled: false, router_id: null, areas: [] } } },
    { id: 'R2', type: 'router', model: 'generic', x: 450, y: 200, label: 'R2', hostname: 'R2',
      ports: [
        { id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.0.12.2', mask: '255.255.255.252' },
        { id: 'Fa0/1', name: 'Fa0/1', state: 'up', ip: '10.0.23.1', mask: '255.255.255.252' },
      ],
      config: { hostname: 'R2', vlans: [], routes: [], ospf: { enabled: false, router_id: null, areas: [] } } },
    { id: 'R3', type: 'router', model: 'generic', x: 800, y: 200, label: 'R3', hostname: 'R3',
      ports: [
        { id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.0.23.2', mask: '255.255.255.252' },
      ],
      config: { hostname: 'R3', vlans: [], routes: [], ospf: { enabled: false, router_id: null, areas: [] } } },
  ],
  links: [
    { id: 'L1', from: { node: 'R1', port: 'Fa0/0' }, to: { node: 'R2', port: 'Fa0/0' }, cable_type: 'copper_straight', state: 'up', bandwidth: 100, latency_ms: 1 },
    { id: 'L2', from: { node: 'R2', port: 'Fa0/1' }, to: { node: 'R3', port: 'Fa0/0' }, cable_type: 'copper_straight', state: 'up', bandwidth: 100, latency_ms: 1 },
  ],
  simulation: { state: 'idle', event_log: [] },
});

export const useLabStore = create((set, get) => ({
  lab: null, topology: null, selectedDevice: null, checkResult: null, loading: false, error: null,

  loadLab(labId, definition, initialTopology) {
    set({ lab: { id: labId, ...(definition || {}) }, topology: initialTopology || emptyTopology(), loading: false, error: null, selectedDevice: null, checkResult: null });
  },
  loadDemo() {
    set({
      lab: { id: 'demo', title: 'Démo · 3 routeurs', level: 'debutant',
        prompt: 'Topologie de démonstration. Clique sur un routeur pour le sélectionner. En production, ce lab est chargé depuis /api/lab/v2/{id}.',
        objectives: ['Vérifier que React Flow affiche 3 routeurs', 'Vérifier les 2 câbles Bézier', 'Cliquer sur Vérifier (retour 404 attendu en mode démo)'] },
      topology: demoTopology(), loading: false, error: null,
    });
  },
  setError(err) { set({ error: String((err && err.message) || err), loading: false }); },
  setLoading(v) { set({ loading: !!v }); },
  updateNodePosition(nodeId, x, y) {
    const topo = get().topology; if (!topo) return;
    set({ topology: { ...topo, nodes: topo.nodes.map(n => n.id === nodeId ? { ...n, x, y } : n) } });
  },
  selectDevice(nodeId) { set({ selectedDevice: nodeId }); },
  setCheckResult(r) { set({ checkResult: r }); },
  clearCheckResult() { set({ checkResult: null }); },
}));
