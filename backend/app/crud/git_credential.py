# /app/crud/git_credential.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.git_credentials import GitCredential
from app.schemas.git_credential import GitCredentialCreate, GitCredentialUpdate

class CRUDGitCredential(CRUDBase[GitCredential, GitCredentialCreate, GitCredentialUpdate]):
    def get_by_user_and_provider(
        self, db: Session, *, user_id: int, provider: str
    ) -> Optional[GitCredential]:
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.provider == provider
        ).first()

    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[GitCredential]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_owner(
        self, db: Session, *, obj_in: GitCredentialCreate, owner_id: int
    ) -> GitCredential:
        """创建新的 Git 凭证，自动关联所有者 ID"""
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        obj_in_data["user_id"] = owner_id
        
        # 处理 token 和 SSH 密钥
        token = obj_in_data.pop("token", None)
        ssh_private_key = obj_in_data.pop("ssh_private_key", None)
        
        db_obj = self.model(**obj_in_data)
        
        # 设置 token 和 SSH 密钥（通过属性设置器自动加密）
        if token is not None:
            db_obj.token = token
        if ssh_private_key is not None:
            db_obj.ssh_private_key = ssh_private_key
            
        db.add(db_obj)
        db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: GitCredential, obj_in: GitCredentialUpdate
    ) -> GitCredential:
        """更新 Git 凭证"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        # 处理 token 和 SSH 密钥
        token = obj_data.pop("token", None)
        ssh_private_key = obj_data.pop("ssh_private_key", None)
        
        # 更新其他字段
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
            
        # 更新 token 和 SSH 密钥（通过属性设置器自动加密）
        if token is not None:
            db_obj.token = token
        if ssh_private_key is not None:
            db_obj.ssh_private_key = ssh_private_key
            
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

git_credential = CRUDGitCredential(GitCredential)