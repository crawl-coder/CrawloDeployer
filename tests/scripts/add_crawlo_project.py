#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 Crawlo 示例项目到数据库的脚本
"""

import sys
import os

# 添加项目路径到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.orm import Session
from backend.app.db.session import SessionLocal
from backend.app import crud, schemas

def add_crawlo_project():
    """添加 Crawlo 示例项目到数据库"""
    db: Session = SessionLocal()
    
    try:
        # 创建项目数据
        project_data = schemas.ProjectCreate(
            name="ofweek_standalone",
            description="Crawlo 示例项目 - OFWeek 爬虫",
            package_path="1",  # 对应 uploaded_projects/1 目录
            owner_id=1,  # 假设用户ID为1
            status="ONLINE",
            version="1.0.0",
            entrypoint="run.py",
            has_requirements=False,
            env_template=None
        )
        
        # 检查项目是否已存在
        existing_project = crud.project.get_by_name(db, name=project_data.name)
        if existing_project:
            print(f"项目 '{project_data.name}' 已存在，ID: {existing_project.id}")
            return existing_project.id
            
        # 创建项目
        project = crud.project.create(db, obj_in=project_data)
        print(f"成功创建项目 '{project.name}'，ID: {project.id}")
        return project.id
        
    except Exception as e:
        print(f"创建项目时出错: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    project_id = add_crawlo_project()
    if project_id:
        print(f"项目创建成功，ID: {project_id}")
    else:
        print("项目创建失败")
        sys.exit(1)