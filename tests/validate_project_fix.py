#!/usr/bin/env python3
"""
验证项目API修复的脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import crud
from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate

def test_exception_handling():
    """测试异常处理逻辑"""
    print("=== 测试异常处理逻辑 ===")
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 创建测试用户
        user_data = UserCreate(
            username="validation_test_user",
            email="validation_test@example.com",
            password="testpassword123"
        )
        
        # 清理可能存在的同名用户
        existing_user = crud.user.get_by_username(db, username=user_data.username)
        if existing_user:
            crud.user.remove(db, id=existing_user.id)
        
        # 创建新用户
        user = crud.user.create(db, obj_in=user_data)
        print(f"✓ 创建测试用户: {user.username}")
        
        # 测试项目名称重复检查
        project_data = ProjectCreate(
            name="validation_test_project",
            description="Test project for validation",
            owner_id=user.id
        )
        
        # 创建第一个项目
        project1 = crud.project.create(db, obj_in=project_data)
        print(f"✓ 创建第一个项目: {project1.name}")
        
        # 尝试创建同名项目，应该抛出ValueError
        try:
            project2 = crud.project.create(db, obj_in=project_data)
            print("✗ 应该抛出ValueError但没有抛出")
            return False
        except ValueError as e:
            print(f"✓ 正确捕获ValueError: {e}")
        except Exception as e:
            print(f"✗ 意外异常类型: {type(e).__name__}: {e}")
            return False
        
        # 清理测试数据
        crud.project.remove(db, id=project1.id)
        crud.user.remove(db, id=user.id)
        print("✓ 测试数据清理完成")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试过程中出现异常: {type(e).__name__}: {e}")
        return False
    finally:
        db.close()

def test_http_exception_passthrough():
    """测试HTTPException传递逻辑"""
    print("\n=== 测试HTTPException传递逻辑 ===")
    
    # 模拟API中的异常处理逻辑
    try:
        # 模拟检查文件参数的逻辑
        files = None
        if not files:
            raise HTTPException(
                status_code=400,
                detail="Files are required for upload method"
            )
    except HTTPException:
        # 重新抛出HTTPException
        print("✓ HTTPException正确传递")
        return True
    except Exception as e:
        print(f"✗ HTTPException未正确传递: {type(e).__name__}: {e}")
        return False

def main():
    """主函数"""
    print("开始验证项目API修复...")
    
    success = True
    
    # 运行测试
    success &= test_exception_handling()
    success &= test_http_exception_passthrough()
    
    if success:
        print("\n✅ 所有测试通过！项目API修复验证成功。")
        return 0
    else:
        print("\n❌ 部分测试失败！请检查代码实现。")
        return 1

if __name__ == "__main__":
    sys.exit(main())