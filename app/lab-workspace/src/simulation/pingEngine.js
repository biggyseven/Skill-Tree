import { useLabStore } from '../store/useLabStore.js';

export async function simulatePing(sourceId, targetIp) {
  const store = useLabStore.getState();
  const topo = store.topology;
  if (!topo) return { success: false, reason: 'No topology loaded' };

  const targetNode = topo.nodes.find(n => 
    (n.ports || []).some(p => p.ip === targetIp)
  );

  if (!targetNode) {
    const res = { success: false, reason: 'Destination host unreachable (IP introuvable)' };
    window.dispatchEvent(new CustomEvent('cli:ping-result', { detail: { result: res } }));
    return res;
  }

  if (targetNode.id === sourceId) {
    const res = { success: true, reason: 'Ping local (self)', hops: 0 };
    window.dispatchEvent(new CustomEvent('cli:ping-result', { detail: { result: res } }));
    return res;
  }

  const path = findPath(topo, sourceId, targetNode.id);
  if (!path) {
    const res = { success: false, reason: 'Destination host unreachable (aucune route)' };
    window.dispatchEvent(new CustomEvent('cli:ping-result', { detail: { result: res } }));
    return res;
  }

  await animatePacket(path, topo);

  const res = { success: true, reason: '5 packets transmitted, 5 received, 0% packet loss', hops: path.length - 1 };
  window.dispatchEvent(new CustomEvent('cli:ping-result', { detail: { result: res } }));
  return res;
}

function findPath(topo, startId, endId) {
  const adj = {};
  topo.links.forEach(l => {
    (adj[l.from.node] = adj[l.from.node] || []).push(l.to.node);
    (adj[l.to.node] = adj[l.to.node] || []).push(l.from.node);
  });

  const queue = [[startId]];
  const visited = new Set();

  while (queue.length > 0) {
    const path = queue.shift();
    const node = path[path.length - 1];
    
    if (node === endId) return path;
    if (!visited.has(node)) {
      visited.add(node);
      const neighbors = adj[node] || [];
      for (const n of neighbors) {
        queue.push([...path, n]);
      }
    }
  }
  return null;
}

function animatePacket(path, topo) {
  return new Promise(resolve => {
    let step = 0;
    const store = useLabStore.getState();
    
    const interval = setInterval(() => {
      if (step >= path.length - 1) {
        clearInterval(interval);
        store.setActivePacket(null);
        resolve();
        return;
      }
      
      const fromId = path[step];
      const toId = path[step + 1];
      store.setActivePacket({ from: fromId, to: toId });
      
      step++;
    }, 600); // 600ms par saut
  });
}
