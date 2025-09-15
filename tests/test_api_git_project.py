#!/usr/bin/env python3
"""
通过API测试Git项目创建功能
"""

import sys
import os
import requests
import time

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import crud
from app.schemas.user import UserCreate

def setup_test_user():
    """设置测试用户"""
    db = SessionLocal()
    try:
        # 创建测试用户
        username = f"api_git_test_user_{int(time.time())}"
        user_data = UserCreate(
            username=username,
            email=f"{username}@example.com",
            password="testpassword123"
        )
        
        # 清理可能存在的同名用户
        existing_user = crud.user.get_by_username(db, username=user_data.username)
        if existing_user:
            crud.user.remove(db, id=existing_user.id)
        
        # 创建新用户
        user = crud.user.create(db, obj_in=user_data)
        print(f"✓ 创建测试用户: {user.username}")
        return user.username, "testpassword123"
    finally:
        db.close()

def test_api_create_git_project(username, password):
    """测试通过API创建Git项目"""
    print("=== 通过API测试创建Git项目 ===")
    
    # 登录获取token
    login_data = {
        'username': username,
        'password': password
    }
    
    response = requests.post('http://localhost:8000/api/v1/auth/login', data=login_data)
    if response.status_code != 200:
        print(f"✗ 登录失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    token_data = response.json()
    token = token_data['access_token']
    print("✓ 用户登录成功")
    
    # 准备项目数据
    project_name = f"api_test_git_project_{int(time.time())}"
    project_data = {
        'name': project_name,
        'description': 'Test project created via API from Git repository',
        'deploy_method': 'git',
        'git_url': 'https://github.com/crawl-coder/Crawlo.git'
    }
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print(f"创建Git项目: {project_name}")
    print(f"Git仓库URL: {project_data['git_url']}")
    
    # 发送创建项目请求
    response = requests.post(
        'http://localhost:8000/api/v1/projects/', 
        data=project_data, 
        headers=headers
    )
    
    if response.status_code == 201:
        project_response = response.json()
        print(f"✓ 项目创建成功: {project_response['name']} (ID: {project_response['id']})")
        print(f"  项目路径: {project_response['package_path']}")
        return True
    else:
        print(f"✗ 项目创建失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False

def cleanup_test_user(username):
    """清理测试用户"""
    db = SessionLocal()
    try:
        user = crud.user.get_by_username(db, username=username)
        if user:
            # 删除用户创建的所有项目
            projects = crud.project.get_multi_by_owner(db, owner_id=user.id)
            for project in projects:
                # 删除项目目录
                if project.package_path and os.path.exists(project.package_path):
                    import shutil
                    shutil.rmtree(project.package_path)
                # 删除项目记录
                crud.project.remove(db, id=project.id)
            
            # 删除用户
            crud.user.remove(db, id=user.id)
            print("✓ 测试用户及项目清理完成")
    finally:
        db.close()

def main():
    """主函数"""
    print("开始通过API测试Git项目创建功能...")
    
    # 设置测试用户
    username, password = setup_test_user()
    
    try:
        # 测试通过API创建Git项目
        success = test_api_create_git_project(username, password)
        
        if success:
            print("\n✅ 通过API创建Git项目测试通过！")
            return 0
        else:
            print("\n❌ 通过API创建Git项目测试失败！")
            return 1
    finally:
        # 清理测试用户
        cleanup_test_user(username)

if __name__ == "__main__":
    sys.exit(main())