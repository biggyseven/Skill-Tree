import { DeviceNode } from './DeviceNode.jsx';

export function PCNode({ data, selected }) {
  return <DeviceNode data={data} selected={selected} kind="pc" title="PC" surface="bg-[var(--s2)]" />;
}
