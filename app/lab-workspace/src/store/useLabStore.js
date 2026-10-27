import { create } from 'zustand';

function normalisePortHandleId(handleId) {
  return String(handleId ?? '').replace(/::(?:source|target)$/, '');
}

/**
 * Recalcule l'état opérationnel d'un câble à partir de ses deux interfaces.
 * Un câble branché n'est pas forcément opérationnel si un port est administrativement OFF.
 */
export function syncPhysicalLinkStates(topology) {
  if (!topology) return topology;
  let changed = false;
  const links = (topology.links || []).map(link => {
    const fromNode = (topology.nodes || []).find(node => node.id === link.from?.node);
    const toNode = (topology.nodes || []).find(node => node.id === link.to?.node);
    const fromPort = (fromNode?.ports || []).find(port => port.id === link.from?.port);
    const toPort = (toNode?.ports || []).find(port => port.id === link.to?.port);

    // Conserve les anciens liens incomplets sans inventer leur état.
    if (!fromPort || !toPort) return link;

    const nextState = fromPort.state === 'up' && toPort.state === 'up' ? 'up' : 'down';
    if (link.state === nextState) return link;
    changed = true;
    return { ...link, state: nextState };
  });

  return changed ? { ...topology, links } : topology;
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
  
  addNode(type, x, y, options = {}) {
    const prefix = String(options.idPrefix || type.charAt(0).toUpperCase() + type.slice(1)).replace(/[^a-zA-Z0-9-]/g, '-');
    const existing = new Set((get().topology?.nodes || []).map(n => n.id));
    const token = crypto.randomUUID().slice(0, 8).toUpperCase();
    let id = prefix + '-' + token;
    while (existing.has(id)) id = prefix + '-' + crypto.randomUUID().slice(0, 8).toUpperCase();

    const defaultCount = type === 'router' ? 2 : type === 'switch' ? 8 : 1;
    const requestedCount = Number(options.portCount);
    const portCount = Number.isInteger(requestedCount) ? Math.max(1, Math.min(48, requestedCount)) : defaultCount;
    const portPrefix = options.portPrefix || (['router', 'switch'].includes(type) ? 'Fa0/' : 'eth');
    const startIndex = type === 'switch' ? 1 : 0;
    const defaultPorts = Array.from({ length: portCount }, (_, i) => {
      const name = ['router', 'switch'].includes(type)
        ? portPrefix + (i + startIndex)
        : portPrefix + i;
      return { id: name, name, state: 'down' };
    });

    const newNode = {
      id,
      type,
      x,
      y,
      label: options.canvasLabel ? `${options.canvasLabel}-${token.slice(0, 3)}` : id,
      model: options.model || 'Modèle générique',
      iconType: options.iconType || type,
      ports: defaultPorts,
      config: { hostname: options.canvasLabel ? `${options.canvasLabel}-${token.slice(0, 3)}` : id },
    };
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

    const updatedTopology = {
      ...topo,
      nodes: topo.nodes.map(n => n.id === nodeId
        ? { ...n, ports: (n.ports || []).map(p => p.id === portId ? { ...p, state: p.state === 'up' ? 'down' : 'up' } : p) }
        : n),
    };
    set({ topology: syncPhysicalLinkStates(updatedTopology), checkResult: null });
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
    const sourcePort = (source?.ports || []).find(p => p.id === sourcePortId);
    const targetPort = (target?.ports || []).find(p => p.id === targetPortId);
    if (!sourcePort || !targetPort) return;
    const newLink = {
      id: 'link-' + crypto.randomUUID(),
      from: { node: connection.source, port: sourcePortId },
      to: { node: connection.target, port: targetPortId },
      cable_type: ({
        cable_straight: 'copper_straight',
        cable_cross: 'copper_crossover',
        fiber: 'fiber',
        fiber_multimode: 'fiber_multimode',
        fiber_singlemode: 'fiber_singlemode',
        console: 'console',
        console_usb: 'console_usb',
        dac: 'dac',
        coaxial: 'coaxial',
        serial_dce: 'serial_dce',
        telephone: 'telephone',
        ethernet_cat6a: 'ethernet_cat6a',
        ethernet_cat8: 'ethernet_cat8',
        cable_poe: 'copper_poe',
        fiber_gpon: 'fiber_gpon',
        fiber_armored: 'fiber_armored',
        fiber_lc_patch: 'fiber_lc_patch',
        console_usb_c: 'console_usb_c',
        serial_rs232: 'serial_rs232',
        dac_qsfp: 'dac_qsfp',
        wireless: 'wireless',
      })[type] || 'copper_straight',
      // Le câble est opérationnel uniquement si les deux interfaces sont ON.
      state: sourcePort.state === 'up' && targetPort.state === 'up' ? 'up' : 'down'
    };
    const updatedTopology = { ...topo, links: [...topo.links, newLink] };
    set({ topology: syncPhysicalLinkStates(updatedTopology), activeTool: 'select', checkResult: null });
  },

  selectDevice(nodeId) { set({ selectedDevice: nodeId }); },
  setCheckResult(r) { set({ checkResult: r }); },
  clearCheckResult() { set({ checkResult: null }); },
}));

