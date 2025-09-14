import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from backend.app.core.config import settings

def check_users():
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    # 查询用户
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, username, email, hashed_password FROM cp_users WHERE username = 'test_user'"))
        users = result.fetchall()
        
        print("数据库中的test_user用户:")
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Hashed Password: {user[3]}")

if __name__ == "__main__":
    check_users()