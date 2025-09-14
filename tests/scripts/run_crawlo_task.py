#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行 Crawlo 任务的脚本
"""

import sys
import os

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app import crud
from backend.app.tasks.crawler_tasks import run_generic_script

def run_crawlo_task(task_id: int):
    """运行指定的 Crawlo 任务"""
    db: Session = SessionLocal()
    
    try:
        # 获取任务
        task = crud.task.get(db, id=task_id)
        if not task:
            print(f"任务 ID {task_id} 不存在")
            return False
            
        # 获取项目信息
        project = crud.project.get(db, id=task.project_id)
        if not project:
            print(f"项目 ID {task.project_id} 不存在")
            return False
            
        print(f"正在运行任务: {task.name}")
        print(f"项目: {project.name}")
        print(f"入口文件: {project.entrypoint}")
        print(f"参数: {task.args}")
        
        # 调用 Celery 任务
        celery_task = run_generic_script.delay(
            original_task_id=task.id,
            project_name=project.package_path,  # 使用 package_path 而不是 name
            entrypoint=project.entrypoint,
            args=task.args,
            env={"RUN_MODE": "manual"}
        )
        
        print(f"Celery 任务已提交，ID: {celery_task.id}")
        return True
        
    except Exception as e:
        print(f"运行任务时出错: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python run_crawlo_task.py <task_id>")
        sys.exit(1)
        
    try:
        task_id = int(sys.argv[1])
        success = run_crawlo_task(task_id)
        if success:
            print("任务运行成功")
        else:
            print("任务运行失败")
            sys.exit(1)
    except ValueError:
        print("错误: 任务 ID 必须是数字")
        sys.exit(1)