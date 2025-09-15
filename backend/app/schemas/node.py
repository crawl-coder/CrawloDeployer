# /app/schemas/node.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.node import NodeStatus, NodeOS


class NodeBase(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    status: NodeStatus
    last_heartbeat: Optional[datetime] = None
    registered_at: datetime
    os: NodeOS
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_gb: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_gb: Optional[float] = None
    disk_usage: Optional[float] = None
    version: Optional[str] = None
    python_version: Optional[str] = None
    tags: Optional[str] = None
    capabilities: Optional[str] = None
    max_concurrency: int = 4
    current_concurrency: int = 0
    public_ip: Optional[str] = None
    agent_port: Optional[int] = None
    physical_host_id: Optional[str] = None
    physical_host_name: Optional[str] = None
    container_id: Optional[str] = None
    instance_name: Optional[str] = None


class NodeCreate(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    os: Optional[NodeOS] = None
    physical_host_id: Optional[str] = None
    physical_host_name: Optional[str] = None
    container_id: Optional[str] = None
    instance_name: Optional[str] = None


class NodeUpdate(BaseModel):
    ip_address: Optional[str] = None
    os: Optional[NodeOS] = None
    os_version: Optional[str] = None
    cpu_cores: Optional[int] = None
    cpu_usage: Optional[float] = None
    memory_gb: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_gb: Optional[float] = None
    disk_usage: Optional[float] = None
    version: Optional[str] = None
    python_version: Optional[str] = None
    tags: Optional[str] = None
    capabilities: Optional[str] = None
    max_concurrency: Optional[int] = None
    public_ip: Optional[str] = None
    agent_port: Optional[int] = None
    physical_host_id: Optional[str] = None
    physical_host_name: Optional[str] = None
    container_id: Optional[str] = None
    instance_name: Optional[str] = None


class NodeOut(NodeBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic V2