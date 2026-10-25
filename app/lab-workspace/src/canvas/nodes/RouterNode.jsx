import { DeviceNode } from './DeviceNode.jsx';
export function RouterNode({ data, selected }) {
  return <DeviceNode data={{...data, type: 'router'}} selected={selected} />;
}
