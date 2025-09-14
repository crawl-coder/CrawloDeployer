import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app import crud
from app.schemas.user import UserCreate
from app.schemas.project import ProjectCreate
from app.db.session import SessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    """创建数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_user(db: Session):
    """创建测试用户"""
    user_data = UserCreate(
        username="test_project_user",
        email="test_project@example.com",
        password="testpassword123"
    )
    
    # 检查用户是否已存在
    user = crud.user.get_by_username(db, username=user_data.username)
    if user:
        # 如果存在则删除
        crud.user.remove(db, id=user.id)
    
    # 创建新用户
    user = crud.user.create(db, obj_in=user_data)
    yield user
    
    # 清理
    user = crud.user.get_by_username(db, username=user_data.username)
    if user:
        crud.user.remove(db, id=user.id)

@pytest.fixture
def auth_token(test_user):
    """获取认证token"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test_project_user",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]

def test_create_project_missing_files(db: Session, test_user, auth_token):
    """测试缺少文件时创建项目应返回400错误"""
    response = client.post(
        "/api/v1/projects/",
        data={
            "name": "test_missing_files_project",
            "description": "Test project missing files",
            "deploy_method": "upload"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # 应该返回400错误，而不是500错误
    assert response.status_code == 400
    assert "Files are required for upload method" in response.json()["detail"]
    
    # 确保项目没有被创建
    project = crud.project.get_by_name(db, name="test_missing_files_project")
    assert project is None

def test_create_project_invalid_method(db: Session, test_user, auth_token):
    """测试无效部署方法应返回400错误"""
    response = client.post(
        "/api/v1/projects/",
        data={
            "name": "test_invalid_method_project",
            "description": "Test project with invalid method",
            "deploy_method": "invalid_method"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # 应该返回400错误
    assert response.status_code == 400
    assert "Invalid deploy method" in response.json()["detail"]
    
    # 确保项目没有被创建
    project = crud.project.get_by_name(db, name="test_invalid_method_project")
    assert project is None

def test_create_project_duplicate_name(db: Session, test_user, auth_token):
    """测试重复项目名称应返回400错误"""
    # 首先创建一个项目
    project_data = ProjectCreate(
        name="duplicate_test_project",
        description="Original project",
        owner_id=test_user.id
    )
    project = crud.project.create(db, obj_in=project_data)
    
    # 尝试创建同名项目
    response = client.post(
        "/api/v1/projects/",
        data={
            "name": "duplicate_test_project",
            "description": "Duplicate project",
            "deploy_method": "upload"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # 应该返回400错误
    assert response.status_code == 400
    assert "Project with this name already exists" in response.json()["detail"]
    
    # 清理
    crud.project.remove(db, id=project.id)