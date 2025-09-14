# /app/api/v1/endpoints/git_credentials.py
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import deps, models, schemas
from app.crud.git_credential import git_credential as crud_git_cred

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=schemas.GitCredentialOut)
def create_git_credential(
    *,
    db: Session = Depends(deps.get_db),
    credential_in: schemas.GitCredentialCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """为当前用户创建 Git 凭据"""
    # 检查是否已存在同提供商的凭据
    existing = crud_git_cred.get_by_user_and_provider(
        db, user_id=current_user.id, provider=credential_in.provider
    )
    if existing:
        raise HTTPException(status_code=400, detail="Credential for this provider already exists")

    # 记录创建凭证的日志
    logger.info(f"User {current_user.username} (ID: {current_user.id}) creating Git credential for provider: {credential_in.provider}")
    
    credential_in_db = crud_git_cred.create_with_owner(
        db, obj_in=credential_in, owner_id=current_user.id
    )
    
    logger.info(f"Successfully created Git credential (ID: {credential_in_db.id}) for user {current_user.username}")
    return credential_in_db


@router.get("/", response_model=List[schemas.GitCredentialOut])
def read_git_credentials(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """获取当前用户的所有 Git 凭据"""
    credentials = crud_git_cred.get_multi_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return credentials


@router.put("/{credential_id}", response_model=schemas.GitCredentialOut)
def update_git_credential(
    *,
    credential_id: int,
    credential_in: schemas.GitCredentialUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """更新 Git 凭据"""
    cred = crud_git_cred.get(db, id=credential_id)
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found")
    if cred.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    cred = crud_git_cred.update(db, db_obj=cred, obj_in=credential_in)
    return cred


@router.delete("/{credential_id}")
def delete_git_credential(
    *,
    credential_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """删除 Git 凭据"""
    cred = crud_git_cred.get(db, id=credential_id)
    if not cred:
        raise HTTPException(status_code=404, detail="Credential not found")
    if cred.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud_git_cred.remove(db, id=credential_id)
    return {"ok": True}