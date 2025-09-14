# /backend/app/api/v1/endpoints/projects.py

from fastapi import APIRouter, Depends, HTTPException, UploadFile, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import tempfile

from app import deps, models, schemas
from app.crud import project as crud_project
from app.services.project import project_service
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    deploy_method: str = Form(...),  # "zip", "upload", "git"
    git_url: Optional[str] = Form(None),
    git_username: Optional[str] = Form(None),
    git_token: Optional[str] = Form(None),
    ssh_key: Optional[str] = Form(None),
    ssh_key_fingerprint: Optional[str] = Form(None),
    files: List[UploadFile] = None,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    创建项目：支持ZIP包上传、文件上传、Git仓库克隆
    """
    # 检查项目名称是否已存在
    if crud_project.get_by_name(db, name=name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists"
        )

    project_in = schemas.ProjectCreate(
        name=name,
        description=description,
        owner_id=current_user.id
    )

    try:
        if deploy_method in ["zip", "upload"]:
            # 对于文件上传，files参数是必需的
            if not files:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Files are required for upload method"
                )
            project = project_service.create_project_from_upload(db, project_in, files)
        elif deploy_method == "git":
            if not git_url:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Git URL is required for git method"
                )
            project = project_service.create_project_from_git(
                db, project_in, git_url, git_username, git_token, ssh_key, ssh_key_fingerprint
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid deploy method"
            )
        
        return project
    except HTTPException:
        # 重新抛出HTTPException，保持原有的状态码和错误信息
        raise
    except ValueError as e:
        # 捕获ValueError并返回400错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 捕获其他异常并返回500错误
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/", response_model=List[schemas.ProjectOut])
def read_projects(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取当前用户的所有项目
    """
    projects = crud_project.get_multi_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return projects


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def read_project(
    *,
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取项目详情
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查权限
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return project


@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(
    *,
    project_id: int,
    project_in: schemas.ProjectUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    更新项目
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查权限
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    project = crud_project.update(db, db_obj=project, obj_in=project_in)
    return project


@router.delete("/{project_id}", response_model=schemas.ProjectOut)
def delete_project(
    *,
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    删除项目
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查权限
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 删除项目目录
    if project.package_path and os.path.exists(project.package_path):
        import shutil
        shutil.rmtree(project.package_path)
    
    project = crud_project.remove(db, id=project_id)
    return project


@router.post("/{project_id}/sync", response_model=dict)
def sync_project_to_nodes(
    *,
    project_id: int,
    node_hostnames: List[str],
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    将项目同步到指定节点
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查权限
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        # 调用项目服务同步项目到节点
        project_service.sync_project_to_nodes(project.name, node_hostnames)
        return {"success": True, "message": f"Project {project.name} synced to nodes successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync project: {str(e)}"
        )


@router.get("/{project_id}/files", response_model=List[str])
def get_project_files(
    *,
    project_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """
    获取项目文件列表
    """
    project = crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 检查权限
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        files = project_service.get_project_files(project.name)
        return files
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project files: {str(e)}"
        )