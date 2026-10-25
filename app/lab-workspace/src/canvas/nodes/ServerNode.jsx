import { DeviceNode } from './DeviceNode.jsx';

export function ServerNode({ data, selected }) {
  return <DeviceNode data={data} selected={selected} kind="server" title="Serveur" surface="bg-[var(--s1)]" />;
}
