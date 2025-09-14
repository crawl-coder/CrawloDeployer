# /app/schemas/git_credential.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GitCredentialBase(BaseModel):
    provider: str
    username: str
    # 注意：我们不会在 Schema 中包含 token，以避免意外泄露

class GitCredentialCreate(GitCredentialBase):
    token: Optional[str] = None  # 创建时需要提供 token
    ssh_private_key: Optional[str] = None  # SSH 私钥
    ssh_key_fingerprint: Optional[str] = None  # SSH 公钥指纹

class GitCredentialUpdate(GitCredentialBase):
    token: Optional[str] = None  # 更新时可选
    ssh_private_key: Optional[str] = None  # SSH 私钥
    ssh_key_fingerprint: Optional[str] = None  # SSH 公钥指纹

class GitCredentialOut(GitCredentialBase):
    id: int
    created_at: datetime
    has_ssh_key: bool  # 是否有SSH密钥
    ssh_key_fingerprint: Optional[str] = None  # SSH公钥指纹

    class Config:
        from_attributes = True