# /app/models/git_credential.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.core.config import settings
from cryptography.fernet import Fernet

class GitCredential(Base):
    __tablename__ = "git_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("cp_users.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # e.g., "github", "gitlab"
    username = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # 加密存储的 Token
    _encrypted_token = Column("encrypted_token", Text, nullable=True)
    # 加密存储的 SSH 私钥
    _encrypted_ssh_key = Column("encrypted_ssh_key", Text, nullable=True)
    # SSH 公钥指纹
    ssh_key_fingerprint = Column(String(100), nullable=True)

    # 建立与 User 的关系
    user = relationship("User", back_populates="git_credentials")

    @property
    def token(self):
        """解密并返回 Token"""
        if self._encrypted_token:
            f = Fernet(settings.ENCRYPTION_KEY.encode())
            return f.decrypt(self._encrypted_token.encode()).decode()
        return None

    @token.setter
    def token(self, raw_token: str):
        """加密 Token 并存储"""
        if raw_token:
            f = Fernet(settings.ENCRYPTION_KEY.encode())
            self._encrypted_token = f.encrypt(raw_token.encode()).decode()
        else:
            self._encrypted_token = None

    @property
    def ssh_private_key(self):
        """解密并返回 SSH 私钥"""
        if self._encrypted_ssh_key:
            f = Fernet(settings.ENCRYPTION_KEY.encode())
            return f.decrypt(self._encrypted_ssh_key.encode()).decode()
        return None

    @ssh_private_key.setter
    def ssh_private_key(self, raw_ssh_key: str):
        """加密 SSH 私钥并存储"""
        if raw_ssh_key:
            f = Fernet(settings.ENCRYPTION_KEY.encode())
            self._encrypted_ssh_key = f.encrypt(raw_ssh_key.encode()).decode()
        else:
            self._encrypted_ssh_key = None

    @property
    def has_ssh_key(self):
        """检查是否有SSH密钥"""
        return self._encrypted_ssh_key is not None