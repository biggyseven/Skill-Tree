import { DeviceNode } from './DeviceNode.jsx';

export function SwitchNode({ data, selected }) {
  return <DeviceNode data={data} selected={selected} kind="switch" title="Switch" surface="bg-[var(--s1)]" />;
}
