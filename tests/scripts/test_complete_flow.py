#!/usr/bin/env python3
"""
测试 CrawloDeployer 系统的完整流程
"""

import requests
import json
import time
import os

# 配置
BASE_URL = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login():
    """用户登录获取访问令牌"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 登录成功，获取访问令牌")
            return token_data["access_token"]
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求异常: {str(e)}")
        return None

def create_project(access_token):
    """创建测试项目"""
    url = f"{BASE_URL}/projects/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 创建测试脚本文件
    test_script_content = 'print("Hello, CrawloDeployer!")'
    
    files = {
        'file': ('test_script.py', test_script_content, 'text/plain')
    }
    
    data = {
        'name': f'test_project_{int(time.time())}',
        'description': 'Test project for complete flow'
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 201:
            project_data = response.json()
            print(f"✅ 项目创建成功: {project_data['name']} (ID: {project_data['id']})")
            return project_data
        else:
            print(f"❌ 项目创建失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 项目创建请求异常: {str(e)}")
        return None

def create_task(access_token, project_id):
    """创建测试任务"""
    url = f"{BASE_URL}/tasks/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "name": f"test_task_{int(time.time())}",
        "project_id": project_id,
        "spider_name": "test_spider",
        "entrypoint": "test_script.py",
        "cron_expression": "0 0 * * *",  # 每天执行一次
        "args": {"arg1": "value1"},
        "is_enabled": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            task_data = response.json()
            print(f"✅ 任务创建成功: {task_data['name']} (ID: {task_data['id']})")
            return task_data
        else:
            print(f"❌ 任务创建失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 任务创建请求异常: {str(e)}")
        return None

def run_task_now(access_token, task_id):
    """立即执行任务"""
    url = f"{BASE_URL}/tasks/{task_id}/run"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            task_run_data = response.json()
            print(f"✅ 任务执行启动成功，执行记录ID: {task_run_data['id']}")
            return task_run_data
        else:
            print(f"❌ 任务执行启动失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 任务执行请求异常: {str(e)}")
        return None

def get_task_runs(access_token):
    """获取任务执行记录"""
    url = f"{BASE_URL}/task-runs/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            task_runs_data = response.json()
            print(f"✅ 获取任务执行记录成功，共 {len(task_runs_data)} 条记录")
            return task_runs_data
        else:
            print(f"❌ 获取任务执行记录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取任务执行记录请求异常: {str(e)}")
        return None

def main():
    """主测试流程"""
    print("🚀 开始测试 CrawloDeployer 系统完整流程")
    
    # 1. 用户登录
    print("\n1. 用户登录")
    access_token = login()
    if not access_token:
        return
    
    # 2. 创建项目
    print("\n2. 创建项目")
    project = create_project(access_token)
    if not project:
        return
    
    # 3. 创建任务
    print("\n3. 创建任务")
    task = create_task(access_token, project["id"])
    if not task:
        return
    
    # 4. 立即执行任务
    print("\n4. 立即执行任务")
    task_run = run_task_now(access_token, task["id"])
    if not task_run:
        return
    
    # 5. 查看任务执行记录
    print("\n5. 查看任务执行记录")
    task_runs = get_task_runs(access_token)
    if task_runs is not None:
        print("✅ 系统核心功能流程测试完成")
    else:
        print("❌ 系统核心功能流程测试失败")

if __name__ == "__main__":
    main()