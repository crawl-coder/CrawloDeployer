# /backend/app/api/v1/endpoints/nodes.py

from fastapi import APIRouter, Depends, Form, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from app import deps
from app import models, schemas
from app.models.node import Node, NodeStatus
from app.crud import node as crud_node

router = APIRouter()


# --- 🔐 私有接口：需要登录 ---
@router.get("/", response_model=schemas.ApiResponse[List[schemas.NodeOut]])
def read_nodes(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    nodes = crud_node.get_multi(db, skip=skip, limit=limit)
    return schemas.ApiResponse(
        success=True,
        data=nodes,
        total=len(nodes)
    )


@router.get("/physical-hosts", response_model=schemas.ApiResponse[List[dict]])
def read_physical_hosts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取所有物理主机列表
    """
    # 查询所有有physical_host_name的节点并去重
    stmt = select(Node.physical_host_name).where(
        Node.physical_host_name.isnot(None)
    ).distinct()
    result = db.execute(stmt)
    physical_hosts = result.scalars().all()
    
    # 为每个物理主机获取详细信息
    hosts_info = []
    for host_name in physical_hosts:
        # 获取该物理主机上的所有节点
        nodes_stmt = select(Node).where(Node.physical_host_name == host_name)
        nodes_result = db.execute(nodes_stmt)
        nodes = nodes_result.scalars().all()
        
        # 获取物理主机的总资源（假设第一个非容器节点是物理主机）
        physical_node = None
        logical_nodes = []
        for node in nodes:
            if not node.container_id and not node.physical_host_id:
                physical_node = node
            else:
                logical_nodes.append(node)
                
        host_info = {
            "physical_host_name": host_name,
            "total_nodes": len(nodes),
            "logical_nodes": len(logical_nodes),
            "cpu_cores": physical_node.cpu_cores if physical_node else None,
            "memory_gb": physical_node.memory_gb if physical_node else None,
            "disk_gb": physical_node.disk_gb if physical_node else None,
            "online_nodes": len([n for n in nodes if n.status == NodeStatus.ONLINE]),
            "offline_nodes": len([n for n in nodes if n.status == NodeStatus.OFFLINE])
        }
        hosts_info.append(host_info)
    
    return schemas.ApiResponse(
        success=True,
        data=hosts_info,
        total=len(hosts_info)
    )


@router.post("/check-resources", response_model=schemas.ApiResponse[dict])
def check_resources(
    *,
    physical_host_name: str = Body(..., embed=True),
    required_cpu_cores: int = Body(1, embed=True),
    required_memory_gb: float = Body(1.0, embed=True),
    required_disk_gb: float = Body(1.0, embed=True),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    检查物理主机是否有足够资源创建新的逻辑节点
    """
    try:
        result = crud_node.check_resources_available(
            db, 
            physical_host_name,
            required_cpu_cores,
            required_memory_gb,
            required_disk_gb
        )
        return schemas.ApiResponse(
            success=True,
            data=result
        )
    except Exception as e:
        return schemas.ApiResponse(
            success=False,
            message=f"资源检查失败: {str(e)}",
            data=None
        )


@router.get("/{node_id}", response_model=schemas.ApiResponse[schemas.NodeOut])
def read_node(
    *,
    node_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    db_node = crud_node.get(db, id=node_id)
    if not db_node:
        return schemas.ApiResponse(
            success=False,
            message="Node not found",
            data=None
        )
    return schemas.ApiResponse(
        success=True,
        data=db_node
    )


@router.post("/", response_model=schemas.ApiResponse[schemas.NodeOut])
def create_node(
    *,
    node_in: schemas.NodeCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    手动添加节点（用于预配置或测试）
    """
    # 检查节点是否已存在
    existing_node = crud_node.get_by_hostname(db, hostname=node_in.hostname)
    if existing_node:
        raise HTTPException(status_code=400, detail="Node with this hostname already exists")
    
    try:
        db_node = crud_node.create(db, obj_in=node_in)
        return schemas.ApiResponse(
            success=True,
            data=db_node,
            message="Node created successfully"
        )
    except Exception as e:
        return schemas.ApiResponse(
            success=False,
            message=f"Failed to create node: {str(e)}",
            data=None
        )


@router.put("/{node_id}", response_model=schemas.ApiResponse[schemas.NodeOut])
def update_node(
    *,
    node_id: int,
    node_in: schemas.NodeUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    更新节点信息
    """
    db_node = crud_node.get(db, id=node_id)
    if not db_node:
        return schemas.ApiResponse(
            success=False,
            message="Node not found",
            data=None
        )
    
    try:
        updated_node = crud_node.update(db, db_obj=db_node, obj_in=node_in)
        return schemas.ApiResponse(
            success=True,
            data=updated_node,
            message="Node updated successfully"
        )
    except Exception as e:
        return schemas.ApiResponse(
            success=False,
            message=f"Failed to update node: {str(e)}",
            data=None
        )


@router.delete("/{node_id}", response_model=schemas.ApiResponse[dict])
def delete_node(
    *,
    node_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    删除节点
    """
    db_node = crud_node.get(db, id=node_id)
    if not db_node:
        return schemas.ApiResponse(
            success=False,
            message="Node not found",
            data=None
        )
    
    try:
        crud_node.remove(db, id=node_id)
        return schemas.ApiResponse(
            success=True,
            data={"node_id": node_id},
            message="Node deleted successfully"
        )
    except Exception as e:
        return schemas.ApiResponse(
            success=False,
            message=f"Failed to delete node: {str(e)}",
            data=None
        )


# --- 🌐 公开接口：Worker 自动上报，无需认证 ---
@router.post("/heartbeat", response_model=schemas.ApiResponse[schemas.NodeOut])
def node_heartbeat(
    *,
    hostname: str = Form(...),
    ip: str = Form(...),
    os: str = Form(None),  # ✅ 新增：接收操作系统类型
    physical_host_id: str = Form(None),  # 物理主机ID
    physical_host_name: str = Form(None),  # 物理主机名
    container_id: str = Form(None),  # 容器ID
    instance_name: str = Form(None),  # 实例名称
    db: Session = Depends(deps.get_db)
):
    """
    Worker 定期上报心跳，无需认证
    """
    try:
        # ✅ 如果未提供 os，可以根据 hostname 或其他逻辑推断（可选）
        if not os:
            # 简单推断
            if "win" in hostname.lower():
                os = "WINDOWS"
            elif "linux" in hostname.lower():
                os = "LINUX"
            else:
                os = "UNKNOWN"  # 或者直接报错

        # 准备节点数据
        node_data = {
            "hostname": hostname,
            "ip_address": ip,
            "os": os,
            "physical_host_id": physical_host_id,
            "physical_host_name": physical_host_name,
            "container_id": container_id,
            "instance_name": instance_name
        }

        db_node = crud_node.register_or_update(db, **node_data)
        return schemas.ApiResponse(
            success=True,
            data=db_node
        )
    except Exception as e:
        return schemas.ApiResponse(
            success=False,
            message=f"Failed to register node: {str(e)}",
            data=None
        )


@router.post("/offline", response_model=schemas.ApiResponse[schemas.NodeOut])
def node_offline(
    *,
    hostname: str = Form(...),
    db: Session = Depends(deps.get_db)
):
    """
    Worker 上报离线状态，无需认证
    """
    try:
        db_node = crud_node.get_by_hostname(db, hostname=hostname)
        if not db_node:
            return schemas.ApiResponse(
                success=False,
                message="Node not found",
                data=None
            )
        
        crud_node.mark_offline(db, hostname=hostname)
        db.refresh(db_node)
        return schemas.ApiResponse(
            success=True,
            data=db_node
        )
    except Exception as e:
        return schemas.ApiResponse(
            success=False,
            message=f"Failed to mark node offline: {str(e)}",
            data=None
        )


# --- 🔐 管理员接口 ---
@router.post("/{node_id}/offline", response_model=schemas.ApiResponse[dict])
def mark_node_offline(
    *,
    node_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
):
    db_node = crud_node.get(db, id=node_id)
    if not db_node:
        return schemas.ApiResponse(
            success=False,
            message="Node not found",
            data=None
        )

    crud_node.mark_offline(db, hostname=db_node.hostname)
    return schemas.ApiResponse(
        success=True,
        data={"node_id": node_id, "status": "OFFLINE"},
        message="Node marked as offline successfully"
    )