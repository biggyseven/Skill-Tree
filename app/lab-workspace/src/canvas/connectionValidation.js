const HANDLE_SUFFIX = /::(?:source|target)$/;

function portId(handleId) {
  return String(handleId ?? '').replace(HANDLE_SUFFIX, '');
}

function getPort(topology, nodeId, handleId) {
  const node = (topology?.nodes || []).find(item => item.id === nodeId);
  const id = portId(handleId);
  return (node?.ports || []).find(port => String(port.id ?? port.name) === id);
}

function portFamily(port) {
  if (!port) return null;
  const text = [port.type, port.media, port.connector, port.name, port.id]
    .filter(Boolean).join(' ').toLowerCase();
  if (/console/.test(text)) return 'console';
  if (/usb/.test(text)) return 'usb';
  if (/serial|rs-?232|v\.35|dce|dte/.test(text)) return 'serial';
  if (/coax|\brf\b/.test(text)) return 'coaxial';
  if (/rj11|telephone|phone|dsl/.test(text)) return 'telephone';
  if (/fiber|fibre|optical|optique|gpon|sfp|qsfp/.test(text)) return 'fiber';
  if (/rj45|ethernet/.test(text)) return 'ethernet';
  return null;
}

function cableFamily(cableType) {
  if (/^console/.test(cableType)) return 'console';
  if (/^serial/.test(cableType)) return 'serial';
  if (cableType === 'coaxial') return 'coaxial';
  if (cableType === 'telephone') return 'telephone';
  if (/^fiber/.test(cableType) || cableType === 'fiber') return 'fiber';
  if (cableType === 'dac' || cableType === 'dac_qsfp') return 'fiber';
  if (cableType === 'wireless') return 'wireless';
  return 'ethernet';
}

const compatibleFamilies = {
  console: new Set(['console', 'usb']),
  serial: new Set(['serial']),
  coaxial: new Set(['coaxial']),
  telephone: new Set(['telephone']),
  fiber: new Set(['fiber']),
  ethernet: new Set(['ethernet']),
  wireless: new Set(['wireless', 'ethernet']),
};

/**
 * Rejects objectively incompatible connections only when a port's physical
 * family is explicitly described. Generic Fa0/eth handles remain permissive
 * because the current topology schema does not identify their transceivers.
 */
export function validateConnection({ connection, topology, cableType }) {
  if (!connection?.source || !connection?.target) {
    return { valid: false, message: 'Sélectionne un port de départ et un port d’arrivée.' };
  }
  if (connection.source === connection.target) {
    return { valid: false, message: 'Relie deux équipements différents : un câble ne peut pas revenir sur le même équipement.' };
  }

  const sourcePort = getPort(topology, connection.source, connection.sourceHandle);
  const targetPort = getPort(topology, connection.target, connection.targetHandle);
  if (!sourcePort || !targetPort) {
    return { valid: false, message: 'Impossible d’identifier un des ports. Sélectionne un point de connexion appartenant à une interface physique.' };
  }

  const sourcePortId = portId(connection.sourceHandle);
  const targetPortId = portId(connection.targetHandle);
  const links = topology?.links || [];
  const sourceBusy = links.some(link =>
    (link.from?.node === connection.source && link.from?.port === sourcePortId) ||
    (link.to?.node === connection.source && link.to?.port === sourcePortId)
  );
  const targetBusy = links.some(link =>
    (link.from?.node === connection.target && link.from?.port === targetPortId) ||
    (link.to?.node === connection.target && link.to?.port === targetPortId)
  );
  if (sourceBusy || targetBusy) {
    const names = [sourceBusy ? (sourcePort.name || sourcePort.id) : null, targetBusy ? (targetPort.name || targetPort.id) : null].filter(Boolean);
    return { valid: false, message: `Le port ${names.join(' et ')} est déjà relié. Utilise un port libre ou supprime d’abord la liaison existante.` };
  }

  const family = cableFamily(String(cableType || 'cable_straight'));
  const allowed = compatibleFamilies[family] || compatibleFamilies.ethernet;
  const mismatches = [
    { port: sourcePort, family: portFamily(sourcePort) },
    { port: targetPort, family: portFamily(targetPort) },
  ].filter(item => item.family && !allowed.has(item.family));

  if (mismatches.length) {
    const details = mismatches.map(item => `${item.port.name || item.port.id} (${item.family})`).join(' et ');
    return { valid: false, message: `Câble incompatible avec ${details}. Choisis un câble correspondant au type physique du port.` };
  }

  return { valid: true, message: '' };
}
