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


test('les commandes access-list, acc-l et acl enregistrent les règles sans préfixe', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  parser.execute('enable');
  parser.execute('configure terminal');

  assert.equal(parser.execute('access-list 100 deny ip host 192.168.1.10 host 10.0.0.5').output, '');
  assert.equal(parser.execute('acc-l 100 permit ip any any').output, '');
  assert.equal(parser.execute('acl 100 remark règle de test').output, '');
  assert.deepEqual(device.config.acls, [
    '100 deny ip host 192.168.1.10 host 10.0.0.5',
    '100 permit ip any any',
    '100 remark règle de test',
  ]);
});

test('ip access-group stocke le numéro ACL sur le port et running-config l’affiche', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  parser.execute('enable');
  parser.execute('configure terminal');
  assert.equal(parser.execute('access-list 100 deny ip host 192.168.1.10 host 10.0.0.5').output, '');
  assert.equal(parser.execute('access-list 100 permit ip any any').output, '');
  parser.execute('interface Fa0/0');

  assert.equal(parser.execute('ip access-group 100 in').output, '');
  assert.equal(device.ports[0].access_group_in, 100);

  parser.execute('end');
  const output = parser.execute('show running-config').output;
  assert.match(output, /access-list 100 deny ip host 192\.168\.1\.10 host 10\.0\.0\.5/);
  assert.match(output, /access-list 100 permit ip any any/);
  assert.match(output, /interface Fa0\/0[\s\S]*ip access-group 100 in/);
});

test('ip access-group refuse une direction ou un numéro invalide', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  enterInterfaceConfig(parser);

  assert.match(parser.execute('ip access-group 100 both').output, /Invalid input/);
  assert.match(parser.execute('ip access-group nope in').output, /Invalid input/);
  assert.equal(device.ports[0].access_group_in, undefined);
});


test('workload CLI enregistre un état structuré typé et l’affiche dans running-config', () => {
  const device = makeDevice();
  const parser = new CLIParser(device);
  parser.execute('enable');
  parser.execute('configure terminal');
  assert.equal(parser.execute('workload database engine postgresql').output, '');
  assert.equal(parser.execute('workload database replication enabled').output, '');
  assert.equal(parser.execute('workload database max_connections 200').output, '');
  assert.deepEqual(device.config.workloads.database, { engine: 'postgresql', replication: true, max_connections: 200 });
  assert.match(parser.execute('workload unknown engine postgresql').output, /Invalid workload setting/);
  parser.execute('end');
  const running = parser.execute('show running-config').output;
  assert.match(running, /workload database engine postgresql/);
  assert.match(running, /workload database replication enabled/);
  assert.match(running, /workload database max_connections 200/);
  assert.match(parser.execute('show workloads').output, /"max_connections": 200/);
});
