import { DeviceNode } from './DeviceNode.jsx';
export function SwitchNode({ data, selected }) {
  return <DeviceNode data={{...data, type: 'switch'}} selected={selected} />;
}
