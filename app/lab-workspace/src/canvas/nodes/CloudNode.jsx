import { DeviceNode } from './DeviceNode.jsx';

export function CloudNode({ data, selected }) {
  return <DeviceNode data={data} selected={selected} kind="cloud" title="Cloud" surface="bg-[var(--s1)]" />;
}
