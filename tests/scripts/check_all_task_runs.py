#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查所有任务运行记录
"""

import sys
import os

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app import models

def check_all_task_runs():
    """检查所有任务运行记录"""
    db: Session = SessionLocal()
    
    try:
        task_runs = db.query(models.TaskRun).all()
        print(f"总共有 {len(task_runs)} 条任务运行记录")
        for tr in task_runs:
            print(f"ID: {tr.id}, 任务ID: {tr.task_id}, Celery任务ID: {tr.celery_task_id}, 状态: {tr.status}")
    except Exception as e:
        print(f"检查任务运行记录时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_all_task_runs()