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
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.flush()
        db.commit()
        db.refresh(db_obj)
        return db_obj

git_credential = CRUDGitCredential(GitCredential)