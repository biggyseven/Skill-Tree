/**
 * Parser CLI Cisco-like.
 * Chaque commande est exécutée sur un objet device (issu du Zustand store).
 * Retourne { output: string }.
 */
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
    const ports = this.device.ports || [];
    return ports.find(p => p.id === name || p.name === name);
  }

  execute(line) {
    const raw = line.trim();
    if (!raw) return { output: '' };
    const tokens = raw.split(/\s+/);
    const cmd = tokens[0].toLowerCase();

    // Globales
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

    // Privileged
    if (this.mode === 'privileged') {
      if (cmd === 'configure' && tokens[1] === 'terminal') {
        this.mode = 'config';
        return { output: 'Enter configuration commands, one per line.  End with CNTL/Z.' };
      }
      if (cmd === 'show') return this.doShow(tokens.slice(1));
      if (cmd === 'write' && tokens[1] === 'memory') return { output: 'Building configuration...\n[OK]' };
    }

    // Config
    if (this.mode === 'config') {
      if (cmd === 'hostname' && tokens[1]) {
        this.device.config.hostname = tokens[1];
        this.device.label = tokens[1];
        return { output: '' };
      }
      if (cmd === 'interface' && tokens[1]) {
        const port = this.findPort(tokens[1]);
        if (!port) return { output: '% Interface not found. Use: show ip interface brief' };
        this.mode = 'interface';
        this.context.interface = tokens[1];
        return { output: '' };
      }
      if (cmd === 'router' && tokens[1] === 'ospf') {
        this.mode = 'router';
        this.context.router_pid = tokens[2] || '1';
        if (!this.device.config.ospf) this.device.config.ospf = { enabled: true, router_id: null, areas: [] };
        else this.device.config.ospf.enabled = true;
        return { output: '' };
      }
    }

    // Interface
    if (this.mode === 'interface') {
      const port = this.findPort(this.context.interface);
      if (!port) {
        this.mode = 'config';
        return { output: '% Interface not found.' };
      }
      if (cmd === 'ip' && tokens[1] === 'address') {
        if (!tokens[2] || !tokens[3]) return { output: '% Incomplete command.' };
        port.ip = tokens[2];
        port.mask = tokens[3];
        port.state = 'up';
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'shutdown') { port.state = 'up'; return { output: '' }; }
      if (cmd === 'shutdown') { port.state = 'down'; return { output: '' }; }
      if (cmd === 'switchport' && tokens[1] === 'mode' && tokens[2]) {
        port.mode = tokens[2];
        return { output: '' };
      }
      if (cmd === 'switchport' && tokens[1] === 'access' && tokens[2] === 'vlan' && tokens[3]) {
        port.vlan = parseInt(tokens[3]);
        return { output: '' };
      }
      if (cmd === 'description' && tokens.length > 1) {
        port.description = tokens.slice(1).join(' ');
        return { output: '' };
      }
    }

    // Router OSPF
    if (this.mode === 'router') {
      if (cmd === 'network' && tokens.length >= 5 && tokens[3] === 'area') {
        const network = tokens[1] + '/' + this.maskToCidr(tokens[2]);
        this.device.config.ospf.areas.push({ area: parseInt(tokens[4]), network });
        return { output: '' };
      }
      if (cmd === 'router-id' && tokens[1]) {
        this.device.config.ospf.router_id = tokens[1];
        return { output: '' };
      }
    }

    return { output: `% Invalid input detected at '^' marker.` };
  }

  doShow(args) {
    if (args[0] === 'running-config') return { output: this.formatRunningConfig() };
    if (args[0] === 'ip' && args[1] === 'interface' && args[2] === 'brief') return { output: this.formatIpIntBrief() };
    if (args[0] === 'ip' && args[1] === 'route') return { output: this.formatIpRoute() };
    if (args[0] === 'vlan' && args[1] === 'brief') return { output: this.formatVlanBrief() };
    return { output: `% No 'show' command found for '${args.join(' ')}'.` };
  }

  formatRunningConfig() {
    const c = this.device.config || {};
    let out = 'Building configuration...\n\nCurrent configuration : 1024 bytes\n!\n';
    out += `hostname ${c.hostname || this.device.id}\n!\n`;
    (this.device.ports || []).forEach(p => {
      out += `interface ${p.name || p.id}\n`;
      if (p.description) out += ` description ${p.description}\n`;
      if (p.mode && p.mode !== 'routed') out += ` switchport mode ${p.mode}\n`;
      if (p.vlan) out += ` switchport access vlan ${p.vlan}\n`;
      if (p.ip && p.mask) out += ` ip address ${p.ip} ${p.mask}\n`;
      out += ` ${p.state === 'up' ? 'no ' : ''}shutdown\n!\n`;
    });
    if (c.routes && c.routes.length) {
      c.routes.forEach(r => { out += `ip route ${r.network} ${r.mask} ${r.next_hop}\n`; });
      out += '!\n';
    }
    if (c.ospf && c.ospf.enabled) {
      out += 'router ospf 1\n';
      if (c.ospf.router_id) out += ` router-id ${c.ospf.router_id}\n`;
      (c.ospf.areas || []).forEach(a => {
        const [net, cidr] = a.network.split('/');
        out += ` network ${net} ${this.cidrToMask(parseInt(cidr))} area ${a.area}\n`;
      });
      out += '!\n';
    }
    out += 'end';
    return out;
  }

  formatIpIntBrief() {
    let out = 'Interface              IP-Address      OK? Method Status                Protocol\n';
    (this.device.ports || []).forEach(p => {
      const ip = p.ip || 'unassigned';
      const status = p.state === 'up' ? 'up' : 'administratively down';
      out += `${(p.name || p.id).padEnd(22)} ${ip.padEnd(15)} YES manual ${status.padEnd(21)} up\n`;
    });
    return out;
  }

  formatIpRoute() {
    let out = 'Codes: C - connected, S - static, O - OSPF\n\nGateway of last resort is not set\n\n';
    (this.device.ports || []).forEach(p => {
      if (p.ip && p.mask) {
        const cidr = this.maskToCidr(p.mask);
        const net = this.getNetwork(p.ip, p.mask);
        out += `C    ${net}/${cidr} is directly connected, ${p.name || p.id}\n`;
      }
    });
    if (this.device.config?.routes) {
      this.device.config.routes.forEach(r => {
        out += `S    ${r.network}/${this.maskToCidr(r.mask)} [1/0] via ${r.next_hop}\n`;
      });
    }
    return out;
  }

  formatVlanBrief() {
    let out = 'VLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    \n';
    if (this.device.config?.vlans) this.device.config.vlans.forEach(v => { out += `${String(v.id).padEnd(4)} ${(v.name || 'VLAN' + v.id).padEnd(32)} active    \n`; });
    return out;
  }

  maskToCidr(mask) { return mask.split('.').map(Number).reduce((acc, oct) => acc + (oct >>> 0).toString(2).split('1').length - 1, 0); }
  cidrToMask(cidr) { return [0, 1, 2, 3].map(i => (0xFF << (8 - (cidr - i * 8) > 0 ? 8 - (cidr - i * 8) : 0)) & 0xFF).join('.'); }
  getNetwork(ip, mask) { const ipP = ip.split('.').map(Number); const mP = mask.split('.').map(Number); return ipP.map((o, i) => o & mP[i]).join('.'); }
}
