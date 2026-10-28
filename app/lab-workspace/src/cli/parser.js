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

function isIPv6Prefix(value) {
  const parts = String(value || '').trim().split('/');
  if (parts.length > 2 || !parts[0].includes(':')) return false;
  if (!/^[0-9a-f:]+$/i.test(parts[0]) || (parts[0].match(/:/g) || []).length < 2) return false;
  if (parts.length === 1) return true;
  if (!/^\d{1,3}$/.test(parts[1])) return false;
  const prefix = Number(parts[1]);
  return prefix >= 0 && prefix <= 128;
}

const WORKLOAD_SETTINGS = {
  "automation": [
    "tool",
    "playbook",
    "idempotent",
    "backup_before_change",
    "error_handling",
    "strict_mode",
    "exit_code_check",
    "plan_review",
    "state_backend",
    "lock_enabled",
    "drift_detection",
    "script",
    "inventory"
  ],
  "security": [
    "ddos_protection",
    "rate_limit_pps",
    "upstream_scrubbing",
    "syn_cookies",
    "blackhole_route",
    "default_input_policy",
    "ssh_allowlist",
    "firewall_backend",
    "tls_enforced"
  ],
  "network": [
    "bridge_name",
    "bridge_stp",
    "native_vlan",
    "vlan",
    "mtu",
    "host_ip",
    "namespace_a",
    "namespace_b",
    "veth_pair",
    "subnet",
    "forwarding",
    "static_route",
    "dns_server",
    "pmtud",
    "jumbo_frames",
    "path_mtu_discovery",
    "next_hop",
    "route_check"
  ],
  "dns": [
    "primary_server",
    "forwarder",
    "record_a",
    "record_cname",
    "search_domain",
    "recursion_enabled",
    "zone_transfer",
    "port",
    "ttl"
  ],
  "linux": [
    "firewall_backend",
    "default_input_policy",
    "ssh_allowlist",
    "ip_forward",
    "audit_rules",
    "log_rotation",
    "sysctl_hardening"
  ],
  "database": [
    "engine",
    "replication",
    "backups",
    "backup_retention_days",
    "tls",
    "max_connections",
    "failover",
    "read_replica",
    "backup_destination",
    "connection_pool"
  ],
  "directory": [
    "protocol",
    "server",
    "mfa",
    "tls",
    "base_dn",
    "domain",
    "gpo",
    "scope",
    "audit_policy",
    "firewall_enabled"
  ],
  "ha": [
    "cluster_name",
    "virtual_ip",
    "quorum",
    "health_check_interval",
    "failover_mode",
    "replica_count"
  ],
  "virtualization": [
    "hypervisor",
    "overcommit",
    "live_migration",
    "network_bridge",
    "storage_pool"
  ],
  "web": [
    "reverse_proxy",
    "tls",
    "healthcheck",
    "backend_pool",
    "sticky_sessions",
    "listen_port",
    "upstream_protocol"
  ],
  "storage": [
    "volume_group",
    "logical_volume",
    "raid_level",
    "snapshot",
    "mountpoint",
    "encryption",
    "redundancy"
  ],
  "monitoring": [
    "exporter",
    "target",
    "alert_cpu_percent",
    "alert_disk_percent",
    "stack",
    "scrape_interval_seconds",
    "alert_rule",
    "dashboard",
    "retention_days",
    "service_discovery"
  ],
  "pipeline": [
    "provider",
    "test_stage",
    "deploy_stage",
    "approval_required",
    "artifact_retention_days",
    "branch",
    "tests",
    "environment",
    "security_scan"
  ],
  "docker": [
    "image",
    "runtime",
    "exposed_port",
    "healthcheck",
    "restart_policy",
    "compose_file",
    "web_replicas",
    "database_volume",
    "network",
    "memory_limit",
    "cpu_limit"
  ],
  "git": [
    "remote",
    "branch",
    "protected_branch",
    "require_review",
    "tag",
    "signed_commits",
    "mainline"
  ],
  "kubernetes": [
    "cluster_name",
    "replicas",
    "network_policy",
    "readiness_probe",
    "persistent_volume",
    "namespace",
    "resource_limits",
    "rolling_update",
    "ingress"
  ],
  "voice": [
    "sip_domain",
    "dial_peer",
    "codec",
    "registration",
    "voice_vlan",
    "qos_profile",
    "emergency_route"
  ],
  "backup": [
    "enabled",
    "retention_days",
    "destination",
    "encryption",
    "restore_tested",
    "schedule"
  ]
};

const WORKLOAD_BOOLEAN_VALUES = {
  enabled: true, enable: true, true: true, on: true, yes: true,
  disabled: false, disable: false, false: false, off: false, no: false,
};

function parseWorkloadValue(rawValue) {
  const value = String(rawValue || '').trim();
  const normalized = value.toLowerCase();
  if (Object.prototype.hasOwnProperty.call(WORKLOAD_BOOLEAN_VALUES, normalized)) {
    return WORKLOAD_BOOLEAN_VALUES[normalized];
  }
  if (/^-?\d+$/.test(value)) return Number(value);
  return value;
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
      case 'dhcp': return h + '(dhcp-config)#';
      case 'class-map': return h + '(config-cmap)#';
      case 'policy': return h + '(config-pmap)#';
      default: return h + '>';
    }
  }

  findPort(name) {
    // IOS accepte les noms d'interfaces sans distinction de majuscules/minuscules.
    // On conserve toutefois l'identifiant d'origine sur l'objet de port.
    const requestedName = String(name || '').trim().toLowerCase();
    return (this.device.ports || []).find(p =>
      String(p.id || '').trim().toLowerCase() === requestedName ||
      String(p.name || '').trim().toLowerCase() === requestedName
    );
  }

  ensureProtocols() {
    if (!this.device.config || typeof this.device.config !== 'object') this.device.config = {};
    if (!this.device.config.protocols || typeof this.device.config.protocols !== 'object') {
      this.device.config.protocols = {};
    }
    return this.device.config.protocols;
  }

  ensureProtocolState(name, initialState = {}) {
    const protocols = this.ensureProtocols();
    if (!protocols[name] || typeof protocols[name] !== 'object') protocols[name] = { ...initialState };
    return protocols[name];
  }

  ensureDhcpPool(name) {
    const dhcp = this.ensureProtocolState('dhcp', { excluded_addresses: [], pools: [] });
    if (!Array.isArray(dhcp.excluded_addresses)) dhcp.excluded_addresses = [];
    if (!Array.isArray(dhcp.pools)) dhcp.pools = [];
    let pool = dhcp.pools.find(item => item.name === name);
    if (!pool) {
      pool = { name, network: null, mask: null, default_router: null, dns_server: null, lease_days: null };
      dhcp.pools.push(pool);
    }
    return pool;
  }

  saveStartupConfig() {
    if (!this.device.config || typeof this.device.config !== 'object') this.device.config = {};
    const snapshot = JSON.parse(JSON.stringify(this.device.config));
    delete snapshot.startup_config_saved;
    delete snapshot.startup_config;
    this.device.startup_config = snapshot;
    this.device.config.startup_config_saved = true;
    return snapshot;
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
      if (['interface', 'router', 'dhcp', 'class-map', 'policy'].includes(this.mode)) this.mode = 'config';
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
      // Accepte la forme complète et l'abréviation Cisco habituelle « conf t ».
      if (['conf', 'config', 'configure'].includes(cmd) &&
          ['t', 'term', 'terminal'].includes(String(tokens[1] || '').toLowerCase())) {
        this.mode = 'config';
        return { output: 'Enter configuration commands, one per line.  End with CNTL/Z.' };
      }
      if (cmd === 'show') return this.doShow(tokens.slice(1));
      if (cmd === 'write' && tokens[1] === 'memory') {
        this.saveStartupConfig();
        return { output: 'Building configuration...\n[OK]' };
      }
      if (cmd === 'copy' && ['run', 'running-config'].includes(tokens[1]) &&
          ['start', 'startup-config'].includes(tokens[2]) && tokens.length === 3) {
        this.saveStartupConfig();
        return { output: 'Destination filename [startup-config]?\nBuilding configuration...\n[OK]' };
      }
      if (cmd === 'reload') return { output: 'System configuration has been modified. Save? [yes/no]: ' };
    }

    // --- MODE CONFIG GLOBAL ---
    if (this.mode === 'config') {
      if (cmd === 'hostname' && tokens[1]) {
        this.device.config.hostname = tokens[1];
        this.device.label = tokens[1];
        return { output: '' };
      }

      // L'état applicatif structuré permet une correction serveur des labs système/cloud.
      if (cmd === 'workload') {
        const domain = String(tokens[1] || '').toLowerCase();
        const setting = String(tokens[2] || '').toLowerCase();
        const rawValue = tokens.slice(3).join(' ').trim();
        if (!domain || !setting || !rawValue || !Array.isArray(WORKLOAD_SETTINGS[domain]) || !WORKLOAD_SETTINGS[domain].includes(setting)) {
          return { output: '% Invalid workload setting. Use workload <domain> <setting> <value> with a supported setting.' };
        }
        if (!this.device.config.workloads || typeof this.device.config.workloads !== 'object' || Array.isArray(this.device.config.workloads)) {
          this.device.config.workloads = {};
        }
        if (!this.device.config.workloads[domain] || typeof this.device.config.workloads[domain] !== 'object' || Array.isArray(this.device.config.workloads[domain])) {
          this.device.config.workloads[domain] = {};
        }
        this.device.config.workloads[domain][setting] = parseWorkloadValue(rawValue);
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
      if (cmd === 'ip' && tokens[1] === 'default-gateway' && tokens[2]) {
        if (!isIPv4Address(tokens[2])) return { output: '% Invalid default gateway IPv4 address.' };
        this.device.config.gateway = tokens[2];
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'ip' && tokens[2] === 'default-gateway') {
        delete this.device.config.gateway;
        return { output: '' };
      }
      if (cmd === 'service' && tokens[1] === 'dhcp') {
        this.device.config.dhcp_enabled = true;
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'service' && tokens[2] === 'dhcp') {
        this.device.config.dhcp_enabled = false;
        return { output: '' };
      }
      if (cmd === 'ip' && tokens[1] === 'dhcp' && tokens[2] === 'excluded-address' && tokens[3]) {
        const dhcp = this.ensureProtocolState('dhcp', { excluded_addresses: [], pools: [] });
        if (!Array.isArray(dhcp.excluded_addresses)) dhcp.excluded_addresses = [];
        const range = { start: tokens[3], end: tokens[4] || tokens[3] };
        if (!dhcp.excluded_addresses.some(item => item.start === range.start && item.end === range.end)) dhcp.excluded_addresses.push(range);
        return { output: '' };
      }
      if (cmd === 'ip' && tokens[1] === 'dhcp' && tokens[2] === 'pool' && tokens[3]) {
        this.ensureDhcpPool(tokens[3]);
        this.context.dhcp_pool = tokens[3];
        this.mode = 'dhcp';
        return { output: '' };
      }
      if (cmd === 'ip' && tokens[1] === 'host' && tokens[2] && tokens[3]) {
        const dns = this.ensureProtocolState('dns', { hosts: [] });
        if (!Array.isArray(dns.hosts)) dns.hosts = [];
        const record = { hostname: tokens[2], address: tokens[3] };
        if (!dns.hosts.some(item => item.hostname === record.hostname && item.address === record.address)) dns.hosts.push(record);
        return { output: '' };
      }
      if (cmd === 'ip' && tokens[1] === 'nat' && tokens[2] === 'inside' && tokens[3] === 'source') {
        if (tokens[4] !== 'list' || !tokens[5] || tokens[6] !== 'interface' || !tokens[7] || tokens.length > 9) {
          return { output: '% Invalid NAT syntax. Use ip nat inside source list <acl> interface <outside-interface> overload.' };
        }
        const nat = this.ensureProtocolState('nat', {});
        nat.acl_number = Number(tokens[5]);
        nat.outside_interface = tokens[7];
        nat.overload = tokens[8] === 'overload';
        return { output: '' };
      }
      if (cmd === 'ntp' && tokens[1] === 'server' && tokens[2]) {
        const ntp = this.ensureProtocolState('ntp', { servers: [] });
        if (!Array.isArray(ntp.servers)) ntp.servers = [];
        if (!ntp.servers.includes(tokens[2])) ntp.servers.push(tokens[2]);
        return { output: '' };
      }
      if (cmd === 'logging' && tokens[1] === 'host' && tokens[2]) {
        const syslog = this.ensureProtocolState('syslog', { hosts: [], trap_severity: null });
        if (!Array.isArray(syslog.hosts)) syslog.hosts = [];
        if (!syslog.hosts.includes(tokens[2])) syslog.hosts.push(tokens[2]);
        return { output: '' };
      }
      if (cmd === 'logging' && tokens[1] === 'trap' && tokens[2]) {
        const syslog = this.ensureProtocolState('syslog', { hosts: [], trap_severity: null });
        syslog.trap_severity = tokens[2].toLowerCase();
        return { output: '' };
      }
      if (cmd === 'spanning-tree' && tokens[1] === 'mode' && tokens[2]) {
        const stp = this.ensureProtocolState('stp', { mode: null, roots: [] });
        stp.enabled = true;
        stp.mode = tokens[2].toLowerCase();
        return { output: '' };
      }
      if (cmd === 'spanning-tree' && tokens[1] === 'vlan' && tokens[2] && tokens[3] === 'root' && ['primary', 'secondary'].includes(tokens[4])) {
        const stp = this.ensureProtocolState('stp', { mode: null, roots: [] });
        if (!Array.isArray(stp.roots)) stp.roots = [];
        const root = { vlan: Number(tokens[2]), role: tokens[4] };
        const index = stp.roots.findIndex(item => item.vlan === root.vlan);
        if (index >= 0) stp.roots[index] = root;
        else stp.roots.push(root);
        return { output: '' };
      }
      if (cmd === 'class-map' && tokens[1]) {
        const matchType = ['match-any', 'match-all'].includes(tokens[1].toLowerCase()) ? tokens[1].toLowerCase() : 'match-all';
        const name = ['match-any', 'match-all'].includes(tokens[1].toLowerCase()) ? tokens[2] : tokens[1];
        if (!name) return { output: '% Invalid class-map syntax.' };
        const qos = this.ensureProtocolState('qos', { class_maps: [], policy_maps: [] });
        if (!Array.isArray(qos.class_maps)) qos.class_maps = [];
        if (!Array.isArray(qos.policy_maps)) qos.policy_maps = [];
        if (!qos.class_maps.some(item => item.name === name)) qos.class_maps.push({ name, match_type: matchType, matches: [] });
        this.context.class_map_name = name;
        this.context.class_map_match_type = matchType;
        this.mode = 'class-map';
        return { output: '' };
      }
      if (cmd === 'policy-map' && tokens[1]) {
        const qos = this.ensureProtocolState('qos', { class_maps: [], policy_maps: [] });
        if (!Array.isArray(qos.policy_maps)) qos.policy_maps = [];
        if (!Array.isArray(qos.class_maps)) qos.class_maps = [];
        if (!qos.policy_maps.some(item => item.name === tokens[1])) qos.policy_maps.push({ name: tokens[1], classes: [] });
        this.context.policy_map_name = tokens[1];
        this.context.policy_class_name = null;
        this.mode = 'policy';
        return { output: '' };
      }
      if (cmd === 'router' && ['bgp', 'eigrp'].includes(String(tokens[1] || '').toLowerCase()) && tokens[2]) {
        const protocol = String(tokens[1]).toLowerCase();
        const protocols = this.ensureProtocols();
        if (protocol === 'bgp') {
          const bgp = protocols.bgp && typeof protocols.bgp === 'object' ? protocols.bgp : {};
          bgp.asn = Number(tokens[2]);
          if (!Array.isArray(bgp.neighbors)) bgp.neighbors = [];
          if (!Array.isArray(bgp.networks)) bgp.networks = [];
          protocols.bgp = bgp;
        } else {
          const eigrp = protocols.eigrp && typeof protocols.eigrp === 'object' ? protocols.eigrp : {};
          eigrp.asn = Number(tokens[2]);
          if (!Array.isArray(eigrp.networks)) eigrp.networks = [];
          if (typeof eigrp.auto_summary !== 'boolean') eigrp.auto_summary = true;
          protocols.eigrp = eigrp;
        }
        this.context.router_protocol = protocol;
        this.context.router_pid = tokens[2];
        this.mode = 'router';
        return { output: '' };
      }
      if (cmd === 'interface' && tokens[1]) {
        const port = this.findPort(tokens[1]);
        if (!port) return { output: `% Interface ${tokens[1]} not found. Available interfaces: ${(this.device.ports || []).map(p => p.name || p.id).join(', ') || 'none'}.` };
        this.mode = 'interface';
        // Garder le nom canonique évite une recherche différente après l'entrée en mode interface.
        this.context.interface = port.name || port.id;
        const subinterfaceMatch = String(port.id || port.name).match(/\.(\d+)$/);
        this.context.subinterface_vlan = this.device.type === 'router' && subinterfaceMatch
          ? Number(subinterfaceMatch[1]) : null;
        if (this.context.subinterface_vlan) {
          if (!this.device.config || typeof this.device.config !== 'object') this.device.config = {};
          if (!this.device.config.subinterfaces || typeof this.device.config.subinterfaces !== 'object') this.device.config.subinterfaces = {};
          const key = `VLAN${this.context.subinterface_vlan}`;
          if (!this.device.config.subinterfaces[key] || typeof this.device.config.subinterfaces[key] !== 'object') {
            this.device.config.subinterfaces[key] = { vlan: this.context.subinterface_vlan, interface_name: this.context.interface, encapsulation: null, ip: null, mask: null };
          } else {
            this.device.config.subinterfaces[key].interface_name = this.context.interface;
          }
        }
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
      if (cmd === 'router' && String(tokens[1] || '').toLowerCase() === 'ospf') {
        this.mode = 'router';
        this.context.router_protocol = 'ospf';
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

    // --- MODE DHCP ---
    if (this.mode === 'dhcp') {
      const pool = this.ensureDhcpPool(this.context.dhcp_pool);
      if (cmd === 'network' && tokens[1] && tokens[2]) { pool.network = tokens[1]; pool.mask = tokens[2]; return { output: '' }; }
      if (cmd === 'default-router' && tokens[1]) { pool.default_router = tokens[1]; return { output: '' }; }
      if (cmd === 'dns-server' && tokens[1]) { pool.dns_server = tokens[1]; return { output: '' }; }
      if (cmd === 'lease' && tokens[1] && /^\d+$/.test(tokens[1]) && Number(tokens[1]) > 0) { pool.lease_days = Number(tokens[1]); return { output: '' }; }
    }

    // --- MODE CLASS MAP ---
    if (this.mode === 'class-map' && cmd === 'match' && tokens[1] === 'dscp' && tokens[2]) {
      const qos = this.ensureProtocolState('qos', { class_maps: [], policy_maps: [] });
      if (!Array.isArray(qos.class_maps)) qos.class_maps = [];
      let classMap = qos.class_maps.find(item => item.name === this.context.class_map_name);
      if (!classMap) {
        classMap = { name: this.context.class_map_name, match_type: this.context.class_map_match_type || 'match-all', matches: [] };
        qos.class_maps.push(classMap);
      }
      if (!Array.isArray(classMap.matches)) classMap.matches = [];
      const match = { type: 'dscp', value: tokens[2].toLowerCase() };
      if (!classMap.matches.some(item => item.type === match.type && item.value === match.value)) classMap.matches.push(match);
      return { output: '' };
    }

    // --- MODE POLICY MAP ---
    if (this.mode === 'policy') {
      const qos = this.ensureProtocolState('qos', { class_maps: [], policy_maps: [] });
      if (!Array.isArray(qos.policy_maps)) qos.policy_maps = [];
      let policy = qos.policy_maps.find(item => item.name === this.context.policy_map_name);
      if (!policy) { policy = { name: this.context.policy_map_name, classes: [] }; qos.policy_maps.push(policy); }
      if (cmd === 'class' && tokens[1]) {
        if (!Array.isArray(policy.classes)) policy.classes = [];
        if (!policy.classes.some(item => item.name === tokens[1])) policy.classes.push({ name: tokens[1] });
        this.context.policy_class_name = tokens[1];
        return { output: '' };
      }
      if (['priority', 'bandwidth'].includes(cmd) && tokens[1] === 'percent' && tokens[2] && /^\d+$/.test(tokens[2])) {
        const value = Number(tokens[2]);
        if (value < 1 || value > 100 || !this.context.policy_class_name) return { output: '% Invalid policy action. Enter a class and a percentage between 1 and 100.' };
        const policyClass = (policy.classes || []).find(item => item.name === this.context.policy_class_name);
        if (!policyClass) return { output: '% Class not found in policy map.' };
        policyClass[cmd === 'priority' ? 'priority_percent' : 'bandwidth_percent'] = value;
        return { output: '' };
      }
      if (cmd === 'set' && tokens[1] === 'dscp' && tokens[2] && this.context.policy_class_name) {
        const policyClass = (policy.classes || []).find(item => item.name === this.context.policy_class_name);
        if (!policyClass) return { output: '% Class not found in policy map.' };
        policyClass.set_dscp = tokens[2].toLowerCase();
        return { output: '' };
      }
    }

    // --- MODE INTERFACE ---
    if (this.mode === 'interface') {
      const port = this.findPort(this.context.interface);
      if (!port) { this.mode = 'config'; return { output: '% Interface not found.' }; }
      
      if (cmd === 'duplex') {
        const mode = String(tokens[1] || '').toLowerCase();
        if (!['auto', 'half', 'full'].includes(mode) || tokens.length !== 2) return { output: '% Invalid duplex mode. Use duplex <auto|half|full>.' };
        port.duplex = mode;
        return { output: '' };
      }
      if (cmd === 'encapsulation' && String(tokens[1] || '').toLowerCase() === 'dot1q' && tokens[2]) {
        if (!this.context.subinterface_vlan) return { output: '% Encapsulation dot1q is valid only on a router subinterface.' };
        const vlan = Number(tokens[2]);
        if (!Number.isInteger(vlan) || vlan !== this.context.subinterface_vlan || vlan < 1 || vlan > 4094) return { output: '% VLAN ID must match the subinterface number.' };
        port.encapsulation = vlan;
        const subinterface = this.device.config?.subinterfaces?.[`VLAN${vlan}`];
        if (subinterface) subinterface.encapsulation = vlan;
        return { output: '' };
      }
      if (cmd === 'ipv6' && tokens[1] === 'address' && tokens[2]) {
        if (!isIPv6Prefix(tokens[2])) return { output: '% Invalid IPv6 address or prefix. Use ipv6 address <address>/<0-128>.' };
        port.ipv6 = tokens[2];
        return { output: '' };
      }
      if (cmd === 'ip' && tokens[1] === 'nat' && ['inside', 'outside'].includes(String(tokens[2] || '').toLowerCase()) && tokens.length === 3) {
        port.nat_role = String(tokens[2]).toLowerCase();
        return { output: '' };
      }
      if (cmd === 'standby' && tokens[1] && /^\d+$/.test(tokens[1])) {
        const group = Number(tokens[1]);
        if (!Array.isArray(port.hsrp)) port.hsrp = [];
        let item = port.hsrp.find(entry => entry.group === group);
        if (!item) { item = { group, virtual_ip: null, priority: 100, preempt: false }; port.hsrp.push(item); }
        if (tokens[2] === 'ip' && tokens[3]) item.virtual_ip = tokens[3];
        else if (tokens[2] === 'priority' && tokens[3] && /^\d+$/.test(tokens[3]) && Number(tokens[3]) >= 1 && Number(tokens[3]) <= 255) item.priority = Number(tokens[3]);
        else if (tokens[2] === 'preempt' && tokens.length === 3) item.preempt = true;
        else return { output: '% Invalid HSRP syntax.' };
        return { output: '' };
      }
      if (cmd === 'spanning-tree' && tokens[1] === 'portfast') {
        if (!port.spanning_tree || typeof port.spanning_tree !== 'object') port.spanning_tree = {};
        port.spanning_tree.portfast = true;
        return { output: '' };
      }
      if (cmd === 'spanning-tree' && tokens[1] === 'bpduguard' && tokens[2] === 'enable') {
        if (!port.spanning_tree || typeof port.spanning_tree !== 'object') port.spanning_tree = {};
        port.spanning_tree.bpduguard = true;
        return { output: '' };
      }
      if (cmd === 'switchport' && tokens[1] === 'port-security') {
        if (!port.port_security || typeof port.port_security !== 'object') port.port_security = {};
        if (tokens.length === 2) { port.port_security.enabled = true; return { output: '' }; }
        if (tokens[2] === 'maximum' && tokens[3] && /^\d+$/.test(tokens[3]) && Number(tokens[3]) >= 1 && Number(tokens[3]) <= 1024) {
          port.port_security.maximum = Number(tokens[3]); return { output: '' };
        }
        if (tokens[2] === 'violation' && ['protect', 'restrict', 'shutdown'].includes(String(tokens[3] || '').toLowerCase()) && tokens.length === 4) {
          port.port_security.violation = String(tokens[3]).toLowerCase(); return { output: '' };
        }
        if (tokens[2] === 'mac-address' && tokens[3] === 'sticky' && tokens.length === 4) {
          port.port_security.sticky = true; return { output: '' };
        }
        if (tokens[2] === 'mac-address' && tokens[3] && /^(?:[0-9a-f]{4}\.){2}[0-9a-f]{4}$/i.test(tokens[3]) && tokens.length === 4) {
          port.port_security.mac_address = tokens[3].toLowerCase(); return { output: '' };
        }
        return { output: '% Invalid port-security syntax.' };
      }
      if (cmd === 'service-policy' && tokens[1] === 'output' && tokens[2]) {
        port.service_policy_out = tokens[2];
        return { output: '' };
      }
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

      if (cmd === 'ip' && tokens[1] === 'ospf' && tokens[2] && tokens[3] === 'area' && tokens[4]) {
        if (!this.device.config.interfaces || typeof this.device.config.interfaces !== 'object') this.device.config.interfaces = {};
        const interfaceConfig = this.device.config.interfaces[port.id] && typeof this.device.config.interfaces[port.id] === 'object'
          ? this.device.config.interfaces[port.id] : {};
        interfaceConfig.ospf_enabled = true;
        interfaceConfig.ospf_process_id = String(tokens[2]);
        interfaceConfig.ospf_area = String(tokens[4]);
        this.device.config.interfaces[port.id] = interfaceConfig;
        port.ospf_enabled = true;
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'ip' && tokens[2] === 'ospf') {
        if (!this.device.config.interfaces || typeof this.device.config.interfaces !== 'object') this.device.config.interfaces = {};
        const interfaceConfig = this.device.config.interfaces[port.id] && typeof this.device.config.interfaces[port.id] === 'object'
          ? this.device.config.interfaces[port.id] : {};
        interfaceConfig.ospf_enabled = false;
        this.device.config.interfaces[port.id] = interfaceConfig;
        port.ospf_enabled = false;
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
        if (this.context.subinterface_vlan) {
          const subinterface = this.device.config?.subinterfaces?.[`VLAN${this.context.subinterface_vlan}`];
          if (subinterface) { subinterface.ip = tokens[2]; subinterface.mask = tokens[3]; }
        }
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'ip' && tokens[2] === 'address') {
        port.ip = null; port.mask = null;
        return { output: '' };
      }
      if (cmd === 'no' && tokens[1] === 'shutdown') { port.state = 'up'; return { output: '' }; }
      if (cmd === 'shutdown') { port.state = 'down'; return { output: '' }; }
      if (cmd === 'switchport' && tokens[1] === 'mode' && tokens[2]) {
        port.mode = tokens[2].toLowerCase();
        if (!this.device.config.interfaces || typeof this.device.config.interfaces !== 'object') this.device.config.interfaces = {};
        const interfaceConfig = this.device.config.interfaces[port.id] && typeof this.device.config.interfaces[port.id] === 'object'
          ? this.device.config.interfaces[port.id] : {};
        interfaceConfig.mode = port.mode;
        this.device.config.interfaces[port.id] = interfaceConfig;
        return { output: '' };
      }
      if (cmd === 'switchport' && tokens[1] === 'access' && tokens[2] === 'vlan' && tokens[3]) {
        const vlan = Number.parseInt(tokens[3], 10);
        if (!Number.isInteger(vlan) || vlan < 1 || vlan > 4094) return { output: '% Invalid VLAN ID.' };
        port.vlan = vlan;
        if (!this.device.config.interfaces || typeof this.device.config.interfaces !== 'object') this.device.config.interfaces = {};
        const interfaceConfig = this.device.config.interfaces[port.id] && typeof this.device.config.interfaces[port.id] === 'object'
          ? this.device.config.interfaces[port.id] : {};
        interfaceConfig.vlan = vlan;
        this.device.config.interfaces[port.id] = interfaceConfig;
        return { output: '' };
      }
      if (cmd === 'description' && tokens.length > 1) { port.description = tokens.slice(1).join(' '); return { output: '' }; }
    }

    // --- MODE ROUTER / ROUTING PROTOCOLS ---
    if (this.mode === 'router') {
      const protocol = this.context.router_protocol || 'ospf';
      if (protocol === 'ospf') {
        if (cmd === 'network' && tokens.length >= 5 && tokens[3] === 'area') {
          const prefixLength = this.wildcardMaskToCidr(tokens[2]);
          this.device.config.ospf.areas.push({ area: Number.parseInt(tokens[4], 10), network: tokens[1] + '/' + prefixLength });
          return { output: '' };
        }
        if (cmd === 'router-id' && tokens[1]) { this.device.config.ospf.router_id = tokens[1]; return { output: '' }; }
      }
      if (protocol === 'bgp') {
        const bgp = this.ensureProtocolState('bgp', { asn: Number(this.context.router_pid || 1), neighbors: [], networks: [] });
        if (!Array.isArray(bgp.neighbors)) bgp.neighbors = [];
        if (!Array.isArray(bgp.networks)) bgp.networks = [];
        if (cmd === 'neighbor' && tokens[1] && tokens[2] === 'remote-as' && tokens[3] && /^\d+$/.test(tokens[3])) {
          const entry = { ip: tokens[1], remote_as: Number(tokens[3]) };
          const index = bgp.neighbors.findIndex(item => item.ip === entry.ip);
          if (index >= 0) bgp.neighbors[index] = entry; else bgp.neighbors.push(entry);
          return { output: '' };
        }
        if (cmd === 'network' && tokens[1] && tokens[2] === 'mask' && tokens[3]) {
          const entry = { network: tokens[1], mask: tokens[3] };
          if (!bgp.networks.some(item => item.network === entry.network && item.mask === entry.mask)) bgp.networks.push(entry);
          return { output: '' };
        }
      }
      if (protocol === 'eigrp') {
        const eigrp = this.ensureProtocolState('eigrp', { asn: Number(this.context.router_pid || 1), networks: [], auto_summary: true });
        if (!Array.isArray(eigrp.networks)) eigrp.networks = [];
        if (cmd === 'network' && tokens[1]) {
          const entry = { network: tokens[1], wildcard: tokens[2] || '0.0.0.0' };
          if (!eigrp.networks.some(item => item.network === entry.network && item.wildcard === entry.wildcard)) eigrp.networks.push(entry);
          return { output: '' };
        }
        if (cmd === 'no' && tokens[1] === 'auto-summary') { eigrp.auto_summary = false; return { output: '' }; }
      }
    }

    return { output: `% Invalid input detected at '^' marker.` };
  }

  doShow(args) {
    if (args[0] === 'running-config') return { output: this.formatRunningConfig() };
    if (args[0] === 'workloads') return { output: JSON.stringify(this.device.config?.workloads || {}, null, 2) };
    if (args[0] === 'ip' && args[1] === 'interface' && args[2] === 'brief') return { output: this.formatIpIntBrief() };
    if (args[0] === 'ip' && args[1] === 'route') return { output: this.formatIpRoute() };
    if (args[0] === 'vlan' && args[1] === 'brief') return { output: this.formatVlanBrief() };
    if (args[0] === 'processes' && args[1] === 'cpu') {
      const cpu = Number(this.device.config?.cpu_utilization ?? this.device.config?.system?.cpu_percent ?? 5);
      return { output: `CPU utilization for five seconds: ${cpu}%/0%; one minute: ${cpu}%; five minutes: ${cpu}%` };
    }
    if (args[0] === 'startup-config') {
      return { output: this.device.startup_config ? JSON.stringify(this.device.startup_config, null, 2) : 'Startup configuration not saved.' };
    }
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
      if (p.encapsulation) out += ` encapsulation dot1q ${p.encapsulation}\n`;
      if (p.duplex) out += ` duplex ${p.duplex}\n`;
      if (p.mode && p.mode !== 'routed') out += ` switchport mode ${p.mode}\n`;
      if (p.vlan) out += ` switchport access vlan ${p.vlan}\n`;
      if (p.port_security?.enabled) {
        out += ' switchport port-security\n';
        if (p.port_security.maximum) out += ` switchport port-security maximum ${p.port_security.maximum}\n`;
        if (p.port_security.violation) out += ` switchport port-security violation ${p.port_security.violation}\n`;
        if (p.port_security.mac_address) out += ` switchport port-security mac-address ${p.port_security.mac_address}\n`;
        if (p.port_security.sticky) out += ' switchport port-security mac-address sticky\n';
      }
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
    // Restitution rejouable de l'état workload pour les contrôles serveur.
    Object.entries(c.workloads || {}).forEach(([domain, fields]) => {
      if (!fields || typeof fields !== 'object' || Array.isArray(fields)) return;
      Object.entries(fields).forEach(([setting, value]) => {
        const printable = typeof value === 'boolean' ? (value ? 'enabled' : 'disabled') : String(value);
        out += `workload ${domain} ${setting} ${printable}\n`;
      });
    });
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
