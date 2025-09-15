# /app/crud/crud_node.py
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from app.crud.base import CRUDBase
from app.models.node import Node, NodeStatus
from app.schemas.node import NodeCreate, NodeUpdate


class CRUDNode(CRUDBase[Node, NodeCreate, NodeUpdate]):
    def get_by_hostname(self, db: Session, *, hostname: str) -> Optional[Node]:
        stmt = select(self.model).where(self.model.hostname == hostname)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    def register_or_update(self, db, *, hostname: str, ip_address: str, os: str, 
                          physical_host_id: str = None, physical_host_name: str = None,
                          container_id: str = None, instance_name: str = None):
        node = self.get_by_hostname(db, hostname=hostname)
        if not node:
            node_in = NodeCreate(
                hostname=hostname, 
                ip_address=ip_address, 
                os=os,  # 修复：确保os是正确的枚举值
                physical_host_id=physical_host_id,
                physical_host_name=physical_host_name,
                container_id=container_id,
                instance_name=instance_name
            )
            node = self.create(db, obj_in=node_in)
        else:
            node_update = NodeUpdate(
                ip_address=ip_address, 
                os=os,  # 修复：确保os是正确的枚举值
                physical_host_id=physical_host_id,
                physical_host_name=physical_host_name,
                container_id=container_id,
                instance_name=instance_name
            )
            node = self.update(db, db_obj=node, obj_in=node_update)
        # 确保显式设置状态为ONLINE
        node.status = NodeStatus.ONLINE
        node.last_heartbeat = datetime.datetime.utcnow()
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    def check_resources_available(self, db: Session, physical_host_name: str, 
                                 required_cpu_cores: int = 0,
                                 required_memory_gb: float = 0.0,
                                 required_disk_gb: float = 0.0) -> dict:
        """
        检查物理节点是否有足够的资源创建新的逻辑节点
        
        Args:
            db: 数据库会话
            physical_host_name: 物理主机名
            required_cpu_cores: 所需CPU核心数
            required_memory_gb: 所需内存大小(GB)
            required_disk_gb: 所需磁盘空间(GB)
            
        Returns:
            dict: 资源检查结果
        """
        # 获取该物理主机上的所有逻辑节点
        stmt = select(self.model).where(
            self.model.physical_host_name == physical_host_name
        )
        result = db.execute(stmt)
        logical_nodes = result.scalars().all()
        
        # 计算已使用的资源
        total_cpu_cores = 0
        total_memory_gb = 0.0
        total_disk_gb = 0.0
        
        for node in logical_nodes:
            if node.cpu_cores:
                total_cpu_cores += node.cpu_cores
            if node.memory_gb:
                total_memory_gb += node.memory_gb
            if node.disk_gb:
                total_disk_gb += node.disk_gb
                
        # 获取物理主机的总资源（假设第一个节点包含物理主机信息）
        physical_node = None
        for node in logical_nodes:
            if not node.container_id and not node.physical_host_id:
                physical_node = node
                break
                
        if not physical_node:
            return {
                "available": False,
                "reason": "未找到物理主机信息",
                "details": {}
            }
            
        # 检查资源是否足够
        available_cpu = (physical_node.cpu_cores or 0) - total_cpu_cores
        available_memory = (physical_node.memory_gb or 0.0) - total_memory_gb
        available_disk = (physical_node.disk_gb or 0.0) - total_disk_gb
        
        is_available = (
            available_cpu >= required_cpu_cores and
            available_memory >= required_memory_gb and
            available_disk >= required_disk_gb
        )
        
        return {
            "available": is_available,
            "reason": "资源足够" if is_available else "资源不足",
            "details": {
                "required_cpu": required_cpu_cores,
                "required_memory": required_memory_gb,
                "required_disk": required_disk_gb,
                "available_cpu": available_cpu,
                "available_memory": available_memory,
                "available_disk": available_disk,
                "total_logical_nodes": len(logical_nodes)
            }
        }

    def heartbeat(self, db: Session, *, hostname: str) -> bool:
        """节点心跳"""
        stmt = update(self.model).where(
            self.model.hostname == hostname
        ).values(
            status=NodeStatus.ONLINE,
            last_heartbeat=func.now()
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0

    def mark_offline(self, db: Session, *, hostname: str) -> None:
        """标记节点离线"""
        stmt = update(self.model).where(
            self.model.hostname == hostname
        ).values(
            status=NodeStatus.OFFLINE
        )
        db.execute(stmt)
        db.commit()


node = CRUDNode(Node)