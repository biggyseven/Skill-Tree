import assert from 'node:assert/strict';
import { test } from 'node:test';
import { CLIParser } from './parser.js';

function makeDevice() {
  return {
    id: 'R1',
    type: 'router',
    config: {
      hostname: 'R1',
      routes: [],
      vlans: [],
      ospf: { enabled: false, router_id: '1.1.1.1', areas: [] },
    },
    ports: [{ id: 'Fa0/0', name: 'Fa0/0', state: 'down', ip: null, mask: null }],
  };
}

function enterInterfaceConfig(parser) {
  parser.execute('enable');
  parser.execute('configure terminal');
  parser.execute('interface Fa0/0');
}

test('configurer une adresse IP ne lève pas automatiquement le shutdown', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  enterInterfaceConfig(parser);

  parser.execute('ip address 10.0.12.1 255.255.255.252');
  assert.equal(device.ports[0].ip, '10.0.12.1');
  assert.equal(device.ports[0].mask, '255.255.255.252');
  assert.equal(device.ports[0].state, 'down');

  parser.execute('no shutdown');
  assert.equal(device.ports[0].state, 'up');
  parser.execute('shutdown');
  assert.equal(device.ports[0].state, 'down');
});

test('la commande OSPF network convertit le wildcard en préfixe et conserve l’area', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  parser.execute('enable');
  parser.execute('configure terminal');
  parser.execute('router ospf 1');
  parser.execute('network 10.0.12.0 0.0.0.3 area 0');

  assert.equal(device.config.ospf.enabled, true);
  assert.deepEqual(device.config.ospf.areas, [{ area: 0, network: '10.0.12.0/30' }]);
});


test('la CLI refuse une adresse IPv4 ou un masque invalide sans modifier le port', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  enterInterfaceConfig(parser);

  const invalidAddress = parser.execute('ip address 999.1.1.1 255.255.255.0');
  assert.match(invalidAddress.output, /Invalid IPv4 address/);
  const invalidMask = parser.execute('ip address 10.0.12.1 255.0.255.0');
  assert.match(invalidMask.output, /Invalid subnet mask/);
  assert.equal(device.ports[0].ip, null);
  assert.equal(device.ports[0].mask, null);
});

test('show ip interface brief affiche un état de protocole cohérent avec celui du port', () => {
  const device = makeDevice();
  device.ports.push({ id: 'Fa0/1', name: 'Fa0/1', state: 'up', ip: '10.0.12.2', mask: '255.255.255.252' });
  const parser = new CLIParser(device);
  parser.execute('enable');

  const output = parser.execute('show ip interface brief').output;
  assert.match(output, /administratively down\s+down/);
  assert.match(output, /10\.0\.12\.2\s+YES manual up\s+up/);
});
