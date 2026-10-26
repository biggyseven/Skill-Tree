/**
 * Parser CLI Cisco-like.
 */
function isIPv4Address(value) {
  const octets = String(value || '').trim().split('.');
  return octets.length === 4 && octets.every(octet =>
    /^\d{1,3}$/.test(octet) && Number(octet) >= 0 && Number(octet) <= 255
  );
}

function isIPv4Mask(value) {
  if (!isIPv4Address(value)) return false;
  const bits = String(value).trim().split('.')
    .map(octet => Number(octet).toString(2).padStart(8, '0'))
    .join('');
  return /^1+0*$/.test(bits);
}

export class CLIParser {
  constructor(device, mode = 'user', context = {}) {
    this.device = device;
    this.mode = mode;
    this.context = context;
  }

  getPrompt() {
    const h = this.device.config?.hostname || this.device.id;
    switch (this.mode) {
      case 'user': return h + '>';
      case 'privileged': return h + '#';
      case 'config': return h + '(config)#';
      case 'interface': return h + '(config-if)#';
      case 'router': return h + '(config-router)#';
      default: return h + '>';
    }
  }

  findPort(name) {
    return (this.device.ports || []).find(p => p.id === name || p.name === name);
  }

  execute(line) {
    const raw = line.trim();
    if (!raw) return { output: '' };
    const tokens = raw.split(/\s+/);
    const cmd = tokens[0].toLowerCase();

    // --- COMMANDES GLOBALES ---
    if (cmd === 'ping' && tokens[1]) {
      import('../simulation/pingEngine.js').then(({ simulatePing }) => { simulatePing(this.device.id, tokens[1]); });
      return { output: `Type escape sequence to abort.\nSending 5, 100-byte ICMP Echos to ${tokens[1]}, timeout is 2 seconds:`, isAsync: true };
    }
    if (cmd === 'exit') {
      if (this.mode === 'interface' || this.mode === 'router') this.mode = 'config';
      else if (this.mode === 'config') this.mode = 'privileged';
      else if (this.mode === 'privileged') this.mode = 'user';
      return { output: '' };
    }
    if (cmd === 'end') {
      if (this.mode !== 'user' && this.mode !== 'privileged') this.mode = 'privileged';
      return { output: '' };
    }
    if (cmd === 'enable') {
      if (this.mode === 'user') { this.mode = 'privileged'; return { output: '' }; }
      return { output: '% Already in privileged mode.' };
    }

    // --- MODE PRIVILEGED ---
    if (this.mode === 'privileged') {
      if (cmd === 'configure' && tokens[1] === 'terminal') {
        this.mode = 'config';
        return { output: 'Enter configuration commands, one per line.  End with CNTL/Z.' };
      }
      if (cmd === 'show') return this.doShow(tokens.slice(1));
      if (cmd === 'write' && tokens[1] === 'memory') return { output: 'Building configuration...\n[OK]' };
      if (cmd === 'reload') return { output: 'System configuration has been modified. Save? [yes/no]: ' };
    }

    // --- MODE CONFIG GLOBAL ---
    if (this.mode === 'config') {
      if (cmd === 'hostname' && tokens[1]) {
        this.device.config.hostname = tokens[1];
        this.device.label = tokens[1];
        return { output: '' };
      }

      // ACL IPv4 numérotées : la règle est stockée sans le préfixe de commande.
      if (['access-list', 'acc-l', 'acl'].includes(cmd)) {
        const action = String(tokens[2] || '').toLowerCase();
        if (!/^\d+$/.test(tokens[1] || '') ||
            !['permit', 'deny', 'remark'].includes(action) ||
            tokens.length < 4) {
          return { output: '% Invalid access-list syntax. Use access-list <number> <permit|deny|remark> ...' };
        }
        if (!Array.isArray(this.device.config.acls)) this.device.config.acls = [];
        const rule = raw.slice(raw.indexOf(tokens[1])).trim();
        if (!this.device.config.acls.includes(rule)) this.device.config.acls.push(rule);
        return { output: '' };
      }
      if (cmd === 'interface' && tokens[1]) {
        const port = this.findPort(tokens[1]);
        if (!port) return { output: '% Interface not found.' };
        this.mode = 'interface';
        this.context.interface = tokens[1];
        return { output: '' };
      }
      if (cmd === 'ip' && tokens[1] === 'route' && tokens.length >= 5) {
        if (!this.device.config.routes) this.device.config.routes = [];
        this.device.config.routes.push({ network: tokens[2], mask: tokens[3], next_hop: tokens[4] });
        return { output: '' };
      }
      if (cmd === 'vlan' && tokens[1]) {
        if (!this.device.config.vlans) this.device.config.vlans = [];
        if (!this.device.config.vlans.find(v => v.id === parseInt(tokens[1]))) {
          this.device.config.vlans.push({ id: parseInt(tokens[1]), name: `VLAN${tokens[1]}` });
        }
        return { output: '' };
      }
      if (cmd === 'router' && tokens[1] === 'ospf') {
        this.mode = 'router';
        this.context.router_pid = tokens[2] || '1';
        if (!this.device.config.ospf) {
          this.device.config.ospf = { enabled: true, router_id: null, areas: [] };
        } else {
          this.device.config.ospf.enabled = true;
          if (!Array.isArray(this.device.config.ospf.areas)) this.device.config.ospf.areas = [];
        }
        return { output: '' };
      }
    }

    // --- MODE INTERFACE ---
    if (this.mode === 'interface') {
      const port = this.findPort(this.context.interface);
      if (!port) { this.mode = 'config'; return { output: '% Interface not found.' }; }
      
      if (cmd === 'ip' && String(tokens[1] || '').toLowerCase() === 'access-group') {
        const aclNumber = Number(tokens[2]);
        const direction = String(tokens[3] || '').toLowerCase();
        if (!Number.isInteger(aclNumber) || aclNumber < 1 || aclNumber > 2147483647 ||
            !['in', 'out'].includes(direction) || tokens.length !== 4) {
          return { output: '% Invalid input. Use ip access-group <number> <in|out>.' };
        }
        port[direction === 'in' ? 'access_group_in' : 'access_group_out'] = aclNumber;
        return { output: '' };
      }

      if (cmd === 'ip' && tokens[1] === 'address' && tokens[2] && tokens[3]) {
        if (!isIPv4Address(tokens[2])) {
          return { output: '% Invalid IPv4 address. Use four octets between 0 and 255.' };
        }
        if (!isIPv4Mask(tokens[3])) {
          return { output: '% Invalid subnet mask. Use a contiguous IPv4 network mask.' };
        }
        port.ip = tokens[2]; port.mask = tokens[3];
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'ip' && tokens[2] === 'address') {
        port.ip = null; port.mask = null;
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'shutdown') { port.state = 'up'; return { output: '' }; }
      if (cmd === 'shutdown') { port.state = 'down'; return { output: '' }; }
      if (cmd === 'switchport' && tokens[1] === 'mode' && tokens[2]) { port.mode = tokens[2]; return { output: '' }; }
      if (cmd === 'switchport' && tokens[1] === 'access' && tokens[2] === 'vlan' && tokens[3]) { port.vlan = parseInt(tokens[3]); return { output: '' }; }
      if (cmd === 'description' && tokens.length > 1) { port.description = tokens.slice(1).join(' '); return { output: '' }; }
    }

    // --- MODE ROUTER OSPF ---
    if (this.mode === 'router') {
      if (cmd === 'network' && tokens.length >= 5 && tokens[3] === 'area') {
        const prefixLength = this.wildcardMaskToCidr(tokens[2]);
        this.device.config.ospf.areas.push({
          area: Number.parseInt(tokens[4], 10),
          network: tokens[1] + '/' + prefixLength,
        });
        return { output: '' };
      }
      if (cmd === 'router-id' && tokens[1]) { this.device.config.ospf.router_id = tokens[1]; return { output: '' }; }
    }

    return { output: `% Invalid input detected at '^' marker.` };
  }

  doShow(args) {
    if (args[0] === 'running-config') return { output: this.formatRunningConfig() };
    if (args[0] === 'ip' && args[1] === 'interface' && args[2] === 'brief') return { output: this.formatIpIntBrief() };
    if (args[0] === 'ip' && args[1] === 'route') return { output: this.formatIpRoute() };
    if (args[0] === 'vlan' && args[1] === 'brief') return { output: this.formatVlanBrief() };
    if (args[0] === 'version') return { output: 'Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.1(4)M4, RELEASE SOFTWARE (fc2)\nSkillTree Edition' };
    if (args[0] === 'interfaces' && args[1]) {
      const p = this.findPort(args[1]);
      if (!p) return { output: `% Invalid interface ${args[1]}` };
      return { output: `${p.name} is ${p.state}, line protocol is ${p.state}\n  Hardware is Fast Ethernet, address is ${p.mac || '0000.0000.0000'}\n  Internet address is ${p.ip ? p.ip + '/' + this.maskToCidr(p.mask) : 'unassigned'}` };
    }
    return { output: `% No 'show' command found for '${args.join(' ')}'.` };
  }

  formatRunningConfig() {
    const c = this.device.config || {};
    let out = 'Building configuration...\n\nCurrent configuration : 1024 bytes\n!\n';
    out += `hostname ${c.hostname || this.device.id}\n!\n`;
    
    // VLANs
    if (c.vlans && c.vlans.length) {
      c.vlans.forEach(v => { out += `vlan ${v.id}\n name ${v.name}\n!\n`; });
    }

    // ACL IPv4 numérotées
    if (Array.isArray(c.acls) && c.acls.length) {
      c.acls.forEach(rule => {
        const text = typeof rule === 'string' ? rule.trim() : '';
        if (text) out += `access-list ${text.startsWith('access-list ') ? text.slice(12) : text}\n`;
      });
      out += '!\n';
    }

    // Interfaces
    (this.device.ports || []).forEach(p => {
      out += `interface ${p.name || p.id}\n`;
      if (p.description) out += ` description ${p.description}\n`;
      if (p.mode && p.mode !== 'routed') out += ` switchport mode ${p.mode}\n`;
      if (p.vlan) out += ` switchport access vlan ${p.vlan}\n`;
      if (p.ip && p.mask) out += ` ip address ${p.ip} ${p.mask}\n`;
      if (p.access_group_in !== undefined && p.access_group_in !== null && p.access_group_in !== '') {
        out += ` ip access-group ${p.access_group_in} in\n`;
      }
      if (p.access_group_out !== undefined && p.access_group_out !== null && p.access_group_out !== '') {
        out += ` ip access-group ${p.access_group_out} out\n`;
      }
      out += ` ${p.state === 'up' ? 'no ' : ''}shutdown\n!\n`;
    });

    // Routes
    if (c.routes && c.routes.length) {
      c.routes.forEach(r => { out += `ip route ${r.network} ${r.mask} ${r.next_hop}\n`; });
      out += '!\n';
    }
    out += 'end';
    return out;
  }

  formatIpIntBrief() {
    let out = 'Interface              IP-Address      OK? Method Status                Protocol\n';
    (this.device.ports || []).forEach(p => {
      out += `${(p.name || p.id).padEnd(22)} ${(p.ip || 'unassigned').padEnd(15)} YES manual ${(p.state === 'up' ? 'up' : 'administratively down').padEnd(21)} ${p.state === 'up' ? 'up' : 'down'}\n`;
    });
    return out;
  }

  formatIpRoute() {
    let out = 'Codes: C - connected, S - static, O - OSPF\n\nGateway of last resort is not set\n\n';
    (this.device.ports || []).forEach(p => {
      if (p.ip && p.mask) out += `C    ${this.getNetwork(p.ip, p.mask)}/${this.maskToCidr(p.mask)} is directly connected, ${p.name || p.id}\n`;
    });
    if (this.device.config?.routes) this.device.config.routes.forEach(r => { out += `S    ${r.network}/${this.maskToCidr(r.mask)} [1/0] via ${r.next_hop}\n`; });
    return out;
  }

  formatVlanBrief() {
    let out = 'VLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    \n';
    if (this.device.config?.vlans) this.device.config.vlans.forEach(v => { out += `${String(v.id).padEnd(4)} ${(v.name || 'VLAN' + v.id).padEnd(32)} active    \n`; });
    return out;
  }

  maskToCidr(mask) {
    return mask.split('.').map(Number).reduce((acc, oct) => acc + (oct >>> 0).toString(2).split('1').length - 1, 0);
  }

  // Cisco OSPF emploie un wildcard (inverse du masque réseau), pas un masque de sous-réseau.
  wildcardMaskToCidr(wildcardMask) {
    const octets = String(wildcardMask).split('.').map(Number);
    if (octets.length !== 4 || octets.some(value => !Number.isInteger(value) || value < 0 || value > 255)) {
      return 0;
    }
    const subnetMask = octets.map(value => 255 - value).join('.');
    return this.maskToCidr(subnetMask);
  }

  getNetwork(ip, mask) {
    const ipP = ip.split('.').map(Number);
    const mP = mask.split('.').map(Number);
    return ipP.map((oct, index) => oct & mP[index]).join('.');
  }
}
