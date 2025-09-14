# /backend/app/services/project.py
import os
import shutil
import subprocess
from typing import Optional
from app.core.config import settings
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy.orm import Session
from app import crud
import tempfile
import zipfile
from pathlib import Path


class ProjectService:
    def __init__(self):
        self.projects_dir = settings.PROJECTS_DIR
        os.makedirs(self.projects_dir, exist_ok=True)

    def create_project_from_upload(self, db: Session, project_in: ProjectCreate, files) -> Project:
        """从上传文件创建项目"""
        # 创建项目记录
        project = crud.project.create(db, obj_in=project_in)
        
        # 创建项目目录
        project_dir = os.path.join(self.projects_dir, project.name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 保存上传的文件
        if files:
            self._save_uploaded_files(project_dir, files, "upload")  # 使用固定值"upload"
        
        # 更新项目路径
        project.package_path = project_dir
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return project

    def create_project_from_git(self, db: Session, project_in: ProjectCreate, git_url: str, 
                               git_username: Optional[str] = None, git_token: Optional[str] = None,
                               ssh_key: Optional[str] = None, ssh_key_fingerprint: Optional[str] = None) -> Project:
        """从Git仓库创建项目"""
        # 创建项目记录
        project = crud.project.create(db, obj_in=project_in)
        
        # 创建项目目录
        project_dir = os.path.join(self.projects_dir, project.name)
        os.makedirs(project_dir, exist_ok=True)
        
        # 克隆Git仓库
        try:
            if ssh_key:
                # 使用SSH密钥克隆
                self._clone_with_ssh(project_dir, git_url, ssh_key)
            else:
                # 使用Token/密码克隆
                self._clone_with_token(project_dir, git_url, git_username, git_token)
            
            # 更新项目路径
            project.package_path = project_dir
            db.add(project)
            db.commit()
            db.refresh(project)
            
            return project
        except Exception as e:
            # 清理失败的项目目录
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            # 删除数据库记录
            db.delete(project)
            db.commit()
            raise e

    def _save_uploaded_files(self, project_dir: str, files, deploy_method: str):
        """保存上传的文件"""
        if deploy_method == "zip":
            # 处理ZIP文件
            zip_file = files[0]  # 假设只有一个ZIP文件
            zip_path = os.path.join(project_dir, zip_file.filename)
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(zip_file.file, buffer)
            
            # 解压ZIP文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(project_dir)
            
            # 删除ZIP文件
            os.remove(zip_path)
        elif deploy_method == "upload":
            # 处理多个文件/文件夹
            for file in files:
                # 获取相对路径（保持文件夹结构）
                # 优先使用webkitRelativePath，如果不存在则使用filename
                relative_path = getattr(file, 'webkitRelativePath', None) or file.filename
                file_path = os.path.join(project_dir, relative_path)
                
                # 确保路径安全，防止路径遍历攻击
                file_path = os.path.abspath(file_path)
                if not file_path.startswith(os.path.abspath(project_dir)):
                    raise ValueError("Invalid file path")
                
                # 创建目录
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 保存文件
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

    def _clone_with_token(self, project_dir: str, git_url: str, username: Optional[str], token: Optional[str]):
        """使用Token/密码克隆Git仓库"""
        if token:
            # 插入Token到URL中
            if "@" in git_url:
                # 已经包含认证信息，替换它
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(git_url)
                netloc = f"{username}:{token}@{parsed.hostname}" if username else f"token:{token}@{parsed.hostname}"
                git_url = urlunparse(parsed._replace(netloc=netloc))
            else:
                # 添加认证信息
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(git_url)
                netloc = f"{username}:{token}@{parsed.hostname}" if username else f"token:{token}@{parsed.hostname}"
                git_url = urlunparse(parsed._replace(netloc=netloc))
        
        # 克隆仓库
        subprocess.run(["git", "clone", git_url, project_dir], check=True, capture_output=True, text=True)

    def _clone_with_ssh(self, project_dir: str, git_url: str, ssh_key: str):
        """使用SSH密钥克隆Git仓库"""
        # 创建临时SSH密钥文件
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".key") as key_file:
            key_file.write(ssh_key)
            key_file_path = key_file.name
        
        try:
            # 设置SSH密钥权限
            os.chmod(key_file_path, 0o600)
            
            # 配置SSH命令
            ssh_command = f"ssh -i {key_file_path} -o StrictHostKeyChecking=no"
            
            # 克隆仓库
            env = os.environ.copy()
            env["GIT_SSH_COMMAND"] = ssh_command
            subprocess.run(["git", "clone", git_url, project_dir], check=True, capture_output=True, text=True, env=env)
        finally:
            # 清理临时SSH密钥文件
            if os.path.exists(key_file_path):
                os.remove(key_file_path)

    def sync_project_to_nodes(self, project_name: str, node_hostnames: list):
        """
        将项目文件同步到指定节点
        这是一个示例方法，实际实现可以根据具体需求调整
        """
        project_dir = os.path.join(self.projects_dir, project_name)
        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"Project directory not found: {project_dir}")
        
        # 这里可以实现具体的文件同步逻辑
        # 例如使用rsync、scp或其他文件同步机制
        # 为了简化，这里只是示例
        for hostname in node_hostnames:
            print(f"Syncing project {project_name} to node {hostname}")
            # 实际实现可能如下：
            # subprocess.run(["rsync", "-avz", project_dir, f"{hostname}:{project_dir}"])
        
        return True

    def get_project_files(self, project_name: str):
        """获取项目文件列表"""
        project_dir = os.path.join(self.projects_dir, project_name)
        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"Project directory not found: {project_dir}")
        
        files = []
        for root, dirs, filenames in os.walk(project_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, project_dir)
                files.append(relative_path)
        
        return files


# 创建全局实例
project_service = ProjectService()