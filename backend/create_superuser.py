import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app import models, crud, schemas
from app.db.session import SessionLocal
from app.core.security import get_password_hash

def create_superuser():
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 检查是否已存在超级用户
        existing_user = crud.user.get_by_username(db, username="admin")
        if existing_user:
            print("超级用户 'admin' 已存在")
            return existing_user
            
        # 创建超级用户
        user_in = schemas.UserCreate(
            username="admin",
            email="admin@example.com",
            password="adminpassword123",
            is_superuser=True
        )
        
        user = crud.user.create(db, obj_in=user_in)
        print(f"超级用户创建成功: {user.username}")
        return user
    except Exception as e:
        print(f"创建超级用户时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()