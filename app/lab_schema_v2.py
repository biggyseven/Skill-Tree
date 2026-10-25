"""Modèles Pydantic du Lab Workspace, schéma v2."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any, Literal
import uuid

from pydantic import BaseModel, Field

_PYDANTIC_V2 = hasattr(BaseModel, "model_dump")


if _PYDANTIC_V2:
    class SchemaModel(BaseModel):
        model_config = {"extra": "ignore", "populate_by_name": True}
else:
    class SchemaModel(BaseModel):
        class Config:
            extra = "ignore"
            allow_population_by_field_name = True


DeviceType = Literal["router", "switch", "pc", "firewall", "server", "cloud"]
PortState = Literal["up", "down"]
PortMode = Literal["routed", "access", "trunk", "down"]
CableType = Literal[
    "copper_straight", "copper_crossover", "fiber", "console", "wireless"
]
RuleOperator = Literal[
    "equals", "not_equals", "contains", "contains_network", "exists", "gt", "lt"
]


class TopologyMetadata(SchemaModel):
    name: str = ""
    author: str = ""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    mode: Literal["lab"] = "lab"


class Port(SchemaModel):
    id: str = ""
    name: str = ""
    state: PortState = "down"
    speed: int = 1000
    mac: str = ""
    mode: PortMode = "down"
    ip: str | None = None
    mask: str | None = None
    vlan: int | None = None
    description: str = ""


class OSPFConfig(SchemaModel):
    enabled: bool = False
    router_id: str = ""
    areas: list[Any] = Field(default_factory=list)


class ServicesConfig(SchemaModel):
    dhcp: Any = None
    dns: Any = None
    nat: Any = None


class DeviceConfig(SchemaModel):
    hostname: str = ""
    vlans: list[Any] = Field(default_factory=list)
    routes: list[dict[str, Any]] = Field(default_factory=list)
    ospf: OSPFConfig = Field(default_factory=OSPFConfig)
    acls: list[Any] = Field(default_factory=list)
    services: ServicesConfig = Field(default_factory=ServicesConfig)


class DeviceRuntime(SchemaModel):
    arp_table: list[Any] = Field(default_factory=list)
    mac_table: list[Any] = Field(default_factory=list)
    routing_table: list[Any] = Field(default_factory=list)


class Device(SchemaModel):
    id: str = ""
    type: DeviceType = "pc"
    model: str = ""
    x: float = 0.0
    y: float = 0.0
    label: str = ""
    ports: list[Port] = Field(default_factory=list)
    config: DeviceConfig = Field(default_factory=DeviceConfig)
    runtime: DeviceRuntime = Field(default_factory=DeviceRuntime)


class LinkEndpoint(SchemaModel):
    node: str = ""
    port: str = ""


class Link(SchemaModel):
    id: str = ""
    from_endpoint: LinkEndpoint = Field(default_factory=LinkEndpoint, alias="from")
    to_endpoint: LinkEndpoint = Field(default_factory=LinkEndpoint, alias="to")
    cable_type: CableType = "copper_straight"
    state: PortState = "up"
    bandwidth: int = 1000
    latency_ms: int = 0


class Simulation(SchemaModel):
    state: str = "idle"
    event_log: list[Any] = Field(default_factory=list)


class Topology(SchemaModel):
    schema_version: Literal[2] = 2
    topology_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: TopologyMetadata = Field(default_factory=TopologyMetadata)
    nodes: list[Device] = Field(default_factory=list)
    links: list[Link] = Field(default_factory=list)
    simulation: Simulation = Field(default_factory=Simulation)


class CheckRule(SchemaModel):
    id: str = ""
    description: str = ""
    device: str = ""
    path: str = ""
    operator: RuleOperator = "equals"
    expected: Any = None


class CheckDefinition(SchemaModel):
    type: Literal["config_assertions", "manual_review"] = "manual_review"
    rules: list[CheckRule] = Field(default_factory=list)
    pass_threshold: float = Field(default=1.0, ge=0.0, le=1.0)
    time_bonus: dict[str, Any] = Field(default_factory=dict)


class LabDefinition(SchemaModel):
    schema_version: int = 2
    id: str = ""
    title: str = ""
    level: str = "débutant"
    module: str = "Général"
    duration_min: int = Field(default=15, ge=0)
    difficulty: str = "débutant"
    prompt: str = ""
    objectives: list[str] = Field(default_factory=list)
    hints: list[str] = Field(default_factory=list)
    initial_topology: Topology = Field(default_factory=Topology)
    device_locks: dict[str, dict[str, Any]] = Field(default_factory=dict)
    check: CheckDefinition = Field(default_factory=CheckDefinition)
    xp_reward: int = Field(default=0, ge=0)
    badges: list[str] = Field(default_factory=list)


class CheckRequest(SchemaModel):
    topology: Topology = Field(default_factory=Topology)


class SubmitRequest(SchemaModel):
    topology: Topology = Field(default_factory=Topology)
    check_result: dict[str, Any] = Field(default_factory=dict)


def model_to_dict(value: Any, *, by_alias: bool = False) -> dict[str, Any]:
    """Sérialisation JSON-compatible avec Pydantic v1 et v2."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=by_alias)
    # BaseModel.dict() conserve les datetime : json() les convertit en ISO-8601.
    return json.loads(value.json(by_alias=by_alias))
