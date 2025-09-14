#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 Crawlo 示例任务到数据库的脚本
"""

import sys
import os

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app import crud, schemas

def add_crawlo_task():
    """添加 Crawlo 示例任务到数据库"""
    db: Session = SessionLocal()
    
    try:
        # 创建任务数据
        task_data = schemas.TaskCreate(
            name="Ofweek Crawlo 爬虫任务",
            project_id=3,  # 我们刚刚创建的项目ID
            spider_name="of_week_standalone",
            cron_expression=None,  # 立即运行，不设置定时
            args={
                "crawlo_command": True,
                "spider_name": "of_week_standalone"
            },
            priority="MEDIUM",
            timeout_seconds=3600,
            max_retries=0,
            notify_on_failure=True,
            notify_on_success=False,
            notification_emails=None
        )
        
        # 创建任务
        task = crud.task.create(db, obj_in=task_data)
        print(f"成功创建任务 '{task.name}'，ID: {task.id}")
        return task.id
        
    except Exception as e:
        print(f"创建任务时出错: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    task_id = add_crawlo_task()
    if task_id:
        print(f"任务创建成功，ID: {task_id}")
    else:
        print("任务创建失败")
        sys.exit(1)