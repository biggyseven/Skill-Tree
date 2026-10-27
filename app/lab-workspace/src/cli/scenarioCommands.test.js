import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { isDeepStrictEqual } from 'node:util';
import { test } from 'node:test';
import { CLIParser } from './parser.js';

function makeDevice(type = 'router') {
  const isSwitch = type === 'switch';
  return {
    id: isSwitch ? 'SW1' : 'R1', type,
    config: { hostname:isSwitch?'SW1':'R1', vlans:[], routes:[], ospf:{enabled:false,router_id:'',areas:[]}, acls:[], services:{dhcp:null,dns:null,nat:null}, protocols:{} },
    ports: isSwitch
      ? [{id:'Fa0/1',name:'Fa0/1',state:'down',mode:'down',ip:null,mask:null,vlan:null},{id:'Fa0/24',name:'Fa0/24',state:'down',mode:'down',ip:null,mask:null,vlan:null}]
      : [{id:'Gi0/0',name:'Gi0/0',state:'down',mode:'routed',ip:null,mask:null},{id:'Gi0/1',name:'Gi0/1',state:'down',mode:'routed',ip:null,mask:null}]
  };
}
function enterConfig(parser) {
  assert.equal(parser.execute('enable').output,'');
  assert.match(parser.execute('configure terminal').output,/Enter configuration/);
}
function run(parser, commands) {
  for (const command of commands) {
    const result = parser.execute(command);
    assert.doesNotMatch(result.output || '', /^% (?:Invalid|Interface not found|Class not found)/, `commande refusée : ${command}`);
  }
}

test('IPv4, VLAN access et trunk écrivent un état structuré', () => {
  const r=makeDevice(); const p=new CLIParser(r); enterConfig(p);
  run(p,['interface Gi0/0','ip address 10.10.10.1 255.255.255.0','no shutdown']);
  assert.deepEqual([r.ports[0].ip,r.ports[0].mask,r.ports[0].state],['10.10.10.1','255.255.255.0','up']);
  const sw=makeDevice('switch'); const sp=new CLIParser(sw); enterConfig(sp);
  run(sp,['vlan 10','interface Fa0/1','switchport mode access','switchport access vlan 10','exit','interface Fa0/24','switchport mode trunk']);
  assert.deepEqual(sw.config.vlans,[{id:10,name:'VLAN10'}]);
  assert.deepEqual([sw.ports[0].mode,sw.ports[0].vlan,sw.ports[1].mode],['access',10,'trunk']);
});

test('route statique, OSPF, BGP et EIGRP produisent des objets vérifiables', () => {
  const r=makeDevice(); const p=new CLIParser(r); enterConfig(p);
  run(p,['ip route 172.16.20.0 255.255.255.0 10.0.0.2','router ospf 10','router-id 1.1.1.1','network 10.10.0.0 0.0.0.255 area 0','end']);
  assert.deepEqual(r.config.routes,[{network:'172.16.20.0',mask:'255.255.255.0',next_hop:'10.0.0.2'}]);
  assert.deepEqual(r.config.ospf.areas,[{area:0,network:'10.10.0.0/24'}]);
  const b=makeDevice();const bp=new CLIParser(b);enterConfig(bp);run(bp,['router bgp 65001','neighbor 192.0.2.2 remote-as 65002','network 10.10.0.0 mask 255.255.0.0']);
  assert.equal(b.config.protocols.bgp.asn,65001);
  assert.deepEqual(b.config.protocols.bgp.neighbors,[{ip:'192.0.2.2',remote_as:65002}]);
  const e=makeDevice();const ep=new CLIParser(e);enterConfig(ep);run(ep,['router eigrp 100','network 10.1.0.0 0.0.255.255','no auto-summary']);
  assert.deepEqual(e.config.protocols.eigrp.networks,[{network:'10.1.0.0',wildcard:'0.0.255.255'}]);
  assert.equal(e.config.protocols.eigrp.auto_summary,false);
});

test('ACL et NAT conservent les règles et les affectations', () => {
  const r=makeDevice();const p=new CLIParser(r);enterConfig(p);
  run(p,['access-list 110 deny ip host 192.168.1.10 host 10.0.0.5','access-list 110 permit ip any any','interface Gi0/0','ip access-group 110 in','exit','access-list 1 permit 10.10.0.0 0.0.255.255','interface Gi0/0','ip nat inside','exit','interface Gi0/1','ip nat outside','exit','ip nat inside source list 1 interface Gi0/1 overload']);
  assert.deepEqual(r.config.acls,['110 deny ip host 192.168.1.10 host 10.0.0.5','110 permit ip any any','1 permit 10.10.0.0 0.0.255.255']);
  assert.equal(r.ports[0].access_group_in,110);
  assert.deepEqual([r.ports[0].nat_role,r.ports[1].nat_role],['inside','outside']);
  assert.deepEqual(r.config.protocols.nat,{acl_number:1,outside_interface:'Gi0/1',overload:true});
});

test('DHCP, DNS, NTP et Syslog écrivent des objets de configuration', () => {
  const r=makeDevice();const p=new CLIParser(r);enterConfig(p);
  run(p,['ip dhcp excluded-address 10.10.20.1 10.10.20.10','ip dhcp pool USERS','network 10.10.20.0 255.255.255.0','default-router 10.10.20.1','dns-server 10.10.20.53','lease 7','exit','ip host intranet.example.test 10.10.30.10','ntp server 192.0.2.123','logging host 192.0.2.50','logging trap informational']);
  assert.deepEqual(r.config.protocols.dhcp.pools,[{name:'USERS',network:'10.10.20.0',mask:'255.255.255.0',default_router:'10.10.20.1',dns_server:'10.10.20.53',lease_days:7}]);
  assert.deepEqual(r.config.protocols.dhcp.excluded_addresses,[{start:'10.10.20.1',end:'10.10.20.10'}]);
  assert.deepEqual(r.config.protocols.dns.hosts,[{hostname:'intranet.example.test',address:'10.10.30.10'}]);
  assert.deepEqual(r.config.protocols.ntp.servers,['192.0.2.123']);
  assert.deepEqual(r.config.protocols.syslog,{hosts:['192.0.2.50'],trap_severity:'informational'});
});

test('IPv6, STP, HSRP et port-security écrivent leurs propriétés', () => {
  const r=makeDevice();const p=new CLIParser(r);enterConfig(p);
  run(p,['interface Gi0/0','ipv6 address 2001:db8:10::1/64','no shutdown','standby 10 ip 10.10.10.254','standby 10 priority 110','standby 10 preempt']);
  assert.equal(r.ports[0].ipv6,'2001:db8:10::1/64');
  assert.deepEqual(r.ports[0].hsrp,[{group:10,virtual_ip:'10.10.10.254',priority:110,preempt:true}]);
  const sw=makeDevice('switch');const sp=new CLIParser(sw);enterConfig(sp);
  run(sp,['spanning-tree mode rapid-pvst','spanning-tree vlan 10 root primary','interface Fa0/1','spanning-tree portfast','spanning-tree bpduguard enable','switchport port-security','switchport port-security maximum 2','switchport port-security mac-address sticky']);
  assert.deepEqual(sw.config.protocols.stp.roots,[{vlan:10,role:'primary'}]);
  assert.equal(sw.config.protocols.stp.mode,'rapid-pvst');
  assert.deepEqual(sw.ports[0].spanning_tree,{portfast:true,bpduguard:true});
  assert.deepEqual(sw.ports[0].port_security,{enabled:true,maximum:2,sticky:true});
});

test('QoS crée une classe, une politique et l’attache au port', () => {
  const r=makeDevice();const p=new CLIParser(r);enterConfig(p);
  run(p,['class-map match-any VOICE','match dscp ef','exit','policy-map VOICE-POLICY','class VOICE','priority percent 20','exit','interface Gi0/0','service-policy output VOICE-POLICY']);
  assert.deepEqual(r.config.protocols.qos.class_maps,[{name:'VOICE',match_type:'match-any',matches:[{type:'dscp',value:'ef'}]}]);
  assert.deepEqual(r.config.protocols.qos.policy_maps,[{name:'VOICE-POLICY',classes:[{name:'VOICE',priority_percent:20}]}]);
  assert.equal(r.ports[0].service_policy_out,'VOICE-POLICY');
});

test('une adresse IPv6 invalide est refusée sans changement du port', () => {
  const r=makeDevice();const p=new CLIParser(r);enterConfig(p);run(p,['interface Gi0/0']);
  const out=p.execute('ipv6 address not-an-ip/64');
  assert.match(out.output,/Invalid IPv6/);
  assert.equal(r.ports[0].ipv6,undefined);
});


const SCENARIO_IDS = [
  'cli-ipv4-interfaces', 'cli-vlan-access', 'cli-vlan-trunk', 'cli-static-routing',
  'cli-ospf-area', 'cli-bgp-neighbor', 'cli-eigrp-network', 'cli-acl-interface',
  'cli-dhcp-pool', 'cli-dns-host-records', 'cli-nat-overload', 'cli-ipv6-interface',
  'cli-stp-hardening', 'cli-hsrp-gateway', 'cli-port-security', 'cli-ntp-syslog',
  'cli-qos-voice-policy'
];

function valueAtPath(root, path) {
  const tokens = path.replace(/\[(\d+)\]/g, '.$1').split('.');
  return tokens.reduce((value, token) => {
    if (value === null || value === undefined) return undefined;
    return value[token];
  }, root);
}

function ruleSatisfied(topology, rule) {
  const device = topology.nodes.find(item => item.id === rule.device || item.label === rule.device || item.config?.hostname === rule.device);
  if (!device) return false;
  const actual = valueAtPath(device, rule.path);
  if (rule.operator === 'equals') return isDeepStrictEqual(actual, rule.expected);
  if (rule.operator === 'contains' && Array.isArray(actual)) return actual.some(item => isDeepStrictEqual(item, rule.expected));
  if (rule.operator === 'contains' && typeof actual === 'string') return actual.includes(String(rule.expected));
  return false;
}

test('les séquences CLI de chacun des 17 labs satisfont leurs assertions serveur après exécution réelle', () => {
  for (const scenarioId of SCENARIO_IDS) {
    const scenario = JSON.parse(readFileSync(new URL(`../../../../labs_v2/${scenarioId}.json`, import.meta.url), 'utf8'));
    const targetMatch = scenario.hints[0].match(/^Cible CLI\s*:\s*([^.]+)\./);
    assert.ok(targetMatch, `${scenarioId}: cible CLI absente`);
    const target = targetMatch[1].trim();
    const commandsHint = scenario.hints.find(item => item.startsWith('Séquence de référence'));
    assert.ok(commandsHint, `${scenarioId}: séquence CLI absente`);
    const commands = commandsHint.replace(/^Séquence de référence\s*:\s*/, '').replace(/\.$/, '').split(/\s;\s/);
    const topology = JSON.parse(JSON.stringify(scenario.initial_topology));
    const device = topology.nodes.find(item => item.id === target);
    assert.ok(device, `${scenarioId}: équipement cible ${target} absent`);
    const parser = new CLIParser(device);

    for (const command of commands) {
      const result = parser.execute(command);
      assert.doesNotMatch(result.output || '', /^% (?:Invalid|Interface not found|Class not found)/,
        `${scenarioId}: commande refusée : ${command}`);
    }
    for (const rule of scenario.check.rules) {
      assert.ok(ruleSatisfied(topology, rule),
        `${scenarioId}: assertion serveur non satisfaite après les commandes : ${rule.id} (${rule.device}.${rule.path})`);
    }
  }
});
