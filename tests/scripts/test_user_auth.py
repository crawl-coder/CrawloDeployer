import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from app import models, crud
from app.db.session import SessionLocal

def test_user_auth(username: str, password: str):
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 使用CRUD方法验证用户
        user = crud.user.authenticate(db, username=username, password=password)
        if user:
            print(f"用户 '{username}' 使用密码 '{password}' 验证成功!")
            return True
        else:
            print(f"用户 '{username}' 使用密码 '{password}' 验证失败")
            return False
    finally:
        db.close()

if __name__ == "__main__":
    # 测试一些常见的密码
    passwords_to_test = [
        "testpassword123",
        "password",
        "123456",
        "test123",
        "test_user",
        "admin",
        "administrator"
    ]
    
    username = "test_user"
    
    print(f"测试用户 '{username}' 的密码验证:")
    for password in passwords_to_test:
        if test_user_auth(username, password):
            break