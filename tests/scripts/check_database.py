#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库连接和表结构的脚本
"""

import sys
import os

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app import models

def check_database():
    """检查数据库连接和表结构"""
    db: Session = SessionLocal()
    
    try:
        # 检查任务表
        task_count = db.query(models.Task).count()
        print(f"任务表记录数: {task_count}")
        
        # 检查项目表
        project_count = db.query(models.Project).count()
        print(f"项目表记录数: {project_count}")
        
        # 检查任务运行表
        task_run_count = db.query(models.TaskRun).count()
        print(f"任务运行表记录数: {task_run_count}")
        
        # 显示一些任务信息
        if task_count > 0:
            tasks = db.query(models.Task).limit(5).all()
            print("\n最近的5个任务:")
            for task in tasks:
                print(f"  - ID: {task.id}, 名称: {task.name}, 项目ID: {task.project_id}")
                
        # 显示一些项目信息
        if project_count > 0:
            projects = db.query(models.Project).limit(5).all()
            print("\n项目列表:")
            for project in projects:
                print(f"  - ID: {project.id}, 名称: {project.name}, 状态: {project.status}")
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_database()