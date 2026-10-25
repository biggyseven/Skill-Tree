import { DeviceNode } from './DeviceNode.jsx';

export function FirewallNode({ data, selected }) {
  return <DeviceNode data={data} selected={selected} kind="firewall" title="Firewall" surface="bg-[var(--s1)]" />;
}
