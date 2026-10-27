import assert from 'node:assert/strict';
import { test } from 'node:test';
import { validateConnection } from './connectionValidation.js';

function topology() {
  return {
    nodes: [
      { id: 'R1', ports: [{ id: 'Fa0/0', name: 'Fa0/0' }, { id: 'Console0', name: 'Console0', type: 'console' }] },
      { id: 'R2', ports: [{ id: 'Fa0/0', name: 'Fa0/0' }, { id: 'SFP1', name: 'SFP1', type: 'fiber' }] },
    ],
    links: [],
  };
}
const connection = (source='R1', target='R2', sourceHandle='Fa0/0::source', targetHandle='Fa0/0::target') =>
  ({ source, target, sourceHandle, targetHandle });

test('autorise une liaison Ethernet entre ports génériques', () => {
  assert.equal(validateConnection({ connection: connection(), topology: topology(), cableType: 'cable_straight' }).valid, true);
});

test('refuse de relier un équipement à lui-même', () => {
  const result = validateConnection({ connection: connection('R1','R1'), topology: topology(), cableType: 'cable_straight' });
  assert.equal(result.valid, false);
  assert.match(result.message, /deux équipements différents/);
});

test('refuse de réutiliser un port déjà connecté', () => {
  const topo = topology();
  topo.links.push({ from: { node: 'R1', port: 'Fa0/0' }, to: { node: 'R2', port: 'Fa0/0' } });
  const result = validateConnection({ connection: connection(), topology: topo, cableType: 'cable_straight' });
  assert.equal(result.valid, false);
  assert.match(result.message, /déjà relié/);
});

test('refuse un câble Ethernet sur un port explicitement console', () => {
  const result = validateConnection({
    connection: connection('R1','R2','Console0::source','Fa0/0::target'),
    topology: topology(), cableType: 'cable_straight',
  });
  assert.equal(result.valid, false);
  assert.match(result.message, /incompatible/);
});

test('refuse une liaison fibre sur un port explicitement RJ45', () => {
  const topo = topology();
  topo.nodes[0].ports[0].type = 'ethernet';
  const result = validateConnection({ connection: connection(), topology: topo, cableType: 'fiber_singlemode' });
  assert.equal(result.valid, false);
  assert.match(result.message, /incompatible/);
});

test('reste permissif lorsque le type physique du port est inconnu', () => {
  const result = validateConnection({
    connection: connection('R1','R2','Fa0/0::source','SFP1::target'),
    topology: topology(), cableType: 'fiber_singlemode',
  });
  assert.equal(result.valid, true);
});
