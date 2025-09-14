#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查任务运行记录的脚本
"""

import sys
import os

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app import crud

def check_task_runs():
    """检查任务运行记录"""
    db: Session = SessionLocal()
    
    try:
        # 获取所有任务运行记录
        task_runs = crud.task_run.get_multi(db, skip=0, limit=100)
        
        print(f"找到 {len(task_runs)} 条任务运行记录:")
        print("-" * 80)
        
        for run in task_runs:
            print(f"ID: {run.id}")
            print(f"任务ID: {run.task_id}")
            print(f"Celery任务ID: {run.celery_task_id}")
            print(f"状态: {run.status}")
            print(f"开始时间: {run.start_time}")
            print(f"结束时间: {run.end_time}")
            print(f"Worker节点: {run.worker_node}")
            print(f"日志输出长度: {len(run.log_output) if run.log_output else 0} 字符")
            print("-" * 80)
            
    except Exception as e:
        print(f"检查任务运行记录时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_task_runs()