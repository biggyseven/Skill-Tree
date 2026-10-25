import { DeviceNode } from './DeviceNode.jsx';

export function RouterNode({ data, selected }) {
  return <DeviceNode data={data} selected={selected} kind="router" title="Routeur" surface="bg-[var(--s1)]" />;
}
