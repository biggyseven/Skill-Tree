import { RouterNode } from './nodes/RouterNode.jsx';
import { SwitchNode } from './nodes/SwitchNode.jsx';
import { PCNode } from './nodes/PCNode.jsx';
import { FirewallNode } from './nodes/FirewallNode.jsx';
import { ServerNode } from './nodes/ServerNode.jsx';
import { CloudNode } from './nodes/CloudNode.jsx';
import { CableEdge } from './edges/CableEdge.jsx';

export const nodeTypes = {
  router: RouterNode,
  switch: SwitchNode,
  pc: PCNode,
  firewall: FirewallNode,
  server: ServerNode,
  cloud: CloudNode,
};

export const edgeTypes = {
  cable: CableEdge,
};
