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

test('la CLI accepte conf t et les noms d’interface quelle que soit la casse', () => {
  const device = makeDevice();
  device.id = 'SW1';
  device.type = 'switch';
  device.config.hostname = 'SW1';
  device.ports[0].id = 'Fa0/7';
  device.ports[0].name = 'Fa0/7';
  const parser = new CLIParser(device);

  parser.execute('enable');
  assert.match(parser.execute('conf t').output, /Enter configuration commands/);
  assert.equal(parser.mode, 'config');

  // Le nom en minuscules doit sélectionner le port enregistré en Fa0/7.
  assert.equal(parser.execute('interface fa0/7').output, '');
  assert.equal(parser.mode, 'interface');
  assert.equal(parser.context.interface, 'Fa0/7');
  assert.equal(parser.execute('switchport access vlan 20').output, '');
  assert.equal(device.ports[0].vlan, 20);

  parser.execute('exit');
  // Les mêmes commandes restent valides en majuscules/mélange de casse.
  assert.equal(parser.execute('INTERFACE FA0/7').output, '');
  assert.equal(parser.context.interface, 'Fa0/7');
  assert.equal(parser.execute('switchport access vlan 20').output, '');
  assert.equal(device.ports[0].vlan, 20);
});

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


test('les commandes War Room réparent shutdown, VLAN, trunk, passerelle, DHCP et OSPF', () => {
  const device = {
    id: 'SW1', type: 'switch',
    config: {
      hostname: 'SW1',
      interfaces: { 'Fa0/7': { mode: 'access', vlan: 1 }, 'Fa0/1': { mode: 'access', vlan: 1 } },
      dhcp_enabled: false,
    },
    ports: [
      { id: 'Fa0/7', name: 'Fa0/7', state: 'down', mode: 'access', vlan: 1 },
      { id: 'Fa0/1', name: 'Fa0/1', state: 'up', mode: 'access', vlan: 1 },
    ],
  };
  const parser = new CLIParser(device);
  parser.execute('enable');
  parser.execute('configure terminal');
  parser.execute('interface Fa0/7');
  assert.equal(parser.execute('no shutdown').output, '');
  assert.equal(device.ports[0].state, 'up');

  assert.equal(parser.execute('switchport access vlan 20').output, '');
  assert.equal(device.ports[0].vlan, 20);
  assert.equal(device.config.interfaces['Fa0/7'].vlan, 20);
  assert.equal(parser.execute('switchport mode trunk').output, '');
  assert.equal(device.ports[0].mode, 'trunk');
  assert.equal(device.config.interfaces['Fa0/7'].mode, 'trunk');

  parser.execute('end');
  parser.execute('configure terminal');
  assert.equal(parser.execute('ip default-gateway 10.20.0.1').output, '');
  assert.equal(device.config.gateway, '10.20.0.1');
  assert.equal(parser.execute('no ip default-gateway').output, '');
  assert.equal(device.config.gateway, undefined);
  assert.equal(parser.execute('no service dhcp').output, '');
  assert.equal(device.config.dhcp_enabled, false);
  assert.equal(parser.execute('service dhcp').output, '');
  assert.equal(device.config.dhcp_enabled, true);

  const router = {
    id: 'R1', type: 'router',
    config: { hostname: 'R1', interfaces: { 'Fa0/0': { ospf_enabled: false } } },
    ports: [{ id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.0.0.1', mask: '255.255.255.0' }],
  };
  const ospf = new CLIParser(router);
  enterInterfaceConfig(ospf);
  assert.equal(ospf.execute('ip ospf 1 area 0').output, '');
  assert.equal(router.config.interfaces['Fa0/0'].ospf_enabled, true);
  assert.equal(router.ports[0].ospf_enabled, true);
  assert.equal(ospf.execute('no ip ospf 1 area 0').output, '');
  assert.equal(router.config.interfaces['Fa0/0'].ospf_enabled, false);
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
  assert.match(parser.execute('show workloads').output, /\"max_connections\": 200/);
});


test('la CLI War Room gère duplex, sous-interface 802.1Q et Port Security complet', () => {
  const router = {
    id: 'R1', type: 'router',
    config: { hostname: 'R1', subinterfaces: { VLAN30: { vlan: 30, interface_name: 'Fa0/0.30', encapsulation: 20, ip: '192.168.20.1', mask: '255.255.255.0' } } },
    ports: [
      { id: 'Fa0/0.30', name: 'Fa0/0.30', state: 'up', ip: '192.168.20.1', mask: '255.255.255.0', encapsulation: 20 },
      { id: 'Fa0/1', name: 'Fa0/1', state: 'up', duplex: 'half' },
    ],
  };
  const cli = new CLIParser(router);
  cli.execute('enable'); cli.execute('configure terminal');
  assert.equal(cli.execute('interface Fa0/0.30').output, '');
  assert.equal(cli.execute('encapsulation dot1q 30').output, '');
  assert.equal(cli.execute('ip address 192.168.30.1 255.255.255.0').output, '');
  assert.equal(router.config.subinterfaces.VLAN30.encapsulation, 30);
  assert.equal(router.config.subinterfaces.VLAN30.ip, '192.168.30.1');
  cli.execute('exit');
  assert.equal(cli.execute('interface Fa0/1').output, '');
  assert.equal(cli.execute('duplex full').output, '');
  assert.equal(router.ports[1].duplex, 'full');

  const sw = { id: 'SW1', type: 'switch', config: { hostname: 'SW1', vlans: [1] }, ports: [{ id: 'Fa0/1', name: 'Fa0/1', state: 'up' }] };
  const sec = new CLIParser(sw);
  sec.execute('enable'); sec.execute('configure terminal'); sec.execute('interface Fa0/1');
  assert.equal(sec.execute('switchport port-security').output, '');
  assert.equal(sec.execute('switchport port-security maximum 1').output, '');
  assert.equal(sec.execute('switchport port-security mac-address 00aa.bbcc.ddee').output, '');
  assert.equal(sec.execute('switchport port-security violation shutdown').output, '');
  assert.deepEqual(sw.ports[0].port_security, { enabled: true, maximum: 1, mac_address: '00aa.bbcc.ddee', violation: 'shutdown' });
});

test('la CLI expose la charge CPU et persiste write memory/copy run start', () => {
  const device = {
    id: 'R1', type: 'router',
    config: { hostname: 'R1-EDGE', cpu_utilization: 100, routes: [{ network: '203.0.113.0', mask: '255.255.255.0', next_hop: '198.51.100.1' }] },
    ports: [{ id: 'Fa0/0', name: 'Fa0/0', state: 'up', ip: '10.50.0.1', mask: '255.255.255.0' }],
  };
  const cli = new CLIParser(device);
  cli.execute('enable');
  assert.match(cli.execute('show processes cpu').output, /100%/);
  assert.match(cli.execute('write memory').output, /\[OK\]/);
  assert.equal(device.config.startup_config_saved, true);
  assert.equal(device.startup_config.hostname, 'R1-EDGE');
  device.config.startup_config_saved = false;
  assert.match(cli.execute('copy run start').output, /\[OK\]/);
  assert.equal(device.config.startup_config_saved, true);
  assert.match(cli.execute('show startup-config').output, /R1-EDGE/);
});
