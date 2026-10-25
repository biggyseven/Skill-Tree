import { DeviceNode } from './DeviceNode.jsx';
export function PCNode({ data, selected }) {
  return <DeviceNode data={{...data, type: 'pc'}} selected={selected} />;
}
