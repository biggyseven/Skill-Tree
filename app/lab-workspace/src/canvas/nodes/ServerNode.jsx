import { DeviceNode } from './DeviceNode.jsx';
export function ServerNode({ data, selected }) {
  return <DeviceNode data={{...data, type: 'server'}} selected={selected} />;
}
