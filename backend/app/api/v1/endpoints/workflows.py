# /backend/app/api/v1/endpoints/workflows.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models
from app.deps import get_db, get_current_active_user
from app.schemas.workflow import Workflow, WorkflowCreate, WorkflowUpdate, WorkflowListResponse
from app.schemas.task import TaskOut as Task

router = APIRouter()


@router.get("/", response_model=WorkflowListResponse)
def read_workflows(
    page: int = 1,
    size: int = 10,
    project_id: int = None,
    name: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve workflows.
    """
    query = db.query(models.Workflow)
    
    # Apply filters
    if project_id:
        query = query.filter(models.Workflow.project_id == project_id)
    if name:
        query = query.filter(models.Workflow.name.contains(name))
    if status:
        query = query.filter(models.Workflow.status == status)
    
    # Calculate pagination
    total = query.count()
    workflows = query.offset((page - 1) * size).limit(size).all()
    
    return WorkflowListResponse(
        items=workflows,
        total=total,
        page=page,
        size=size
    )


@router.post("/", response_model=Workflow)
def create_workflow(
    *,
    db: Session = Depends(get_db),
    workflow_in: WorkflowCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create new workflow.
    """
    # Check if workflow with same name already exists in the project
    workflow = crud.workflow.get_by_name_and_project(
        db, name=workflow_in.name, project_id=workflow_in.project_id
    )
    if workflow:
        raise HTTPException(
            status_code=400,
            detail="Workflow with this name already exists in the project"
        )
    
    workflow = crud.workflow.create(db, obj_in=workflow_in)
    return workflow


@router.get("/{id}", response_model=Workflow)
def read_workflow(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get workflow by ID.
    """
    workflow = crud.workflow.get(db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check if user has access to the project this workflow belongs to
    project = crud.project.get(db, id=workflow.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return workflow


@router.put("/{id}", response_model=Workflow)
def update_workflow(
    *,
    db: Session = Depends(get_db),
    id: int,
    workflow_in: WorkflowUpdate,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a workflow.
    """
    workflow = crud.workflow.get(db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check if workflow with same name already exists in the project (if name is being updated)
    if workflow_in.name and workflow_in.name != workflow.name:
        existing_workflow = crud.workflow.get_by_name_and_project(
            db, name=workflow_in.name, project_id=workflow.project_id
        )
        if existing_workflow:
            raise HTTPException(
                status_code=400,
                detail="Workflow with this name already exists in the project"
            )
    
    workflow = crud.workflow.update(db, db_obj=workflow, obj_in=workflow_in)
    return workflow


@router.delete("/{id}")
def delete_workflow(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a workflow.
    """
    workflow = crud.workflow.get(db, id=id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    crud.workflow.remove(db, id=id)
    return {"message": "Workflow deleted successfully"}


@router.get("/{workflow_id}/tasks", response_model=List[Task])
def read_workflow_tasks(
    *,
    db: Session = Depends(get_db),
    workflow_id: int,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get tasks for a workflow.
    """
    workflow = crud.workflow.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get workflow tasks
    workflow_tasks = db.query(models.WorkflowTask).filter(
        models.WorkflowTask.workflow_id == workflow_id
    ).all()
    
    # Get actual tasks
    task_ids = [wt.task_id for wt in workflow_tasks]
    tasks = db.query(models.Task).filter(models.Task.id.in_(task_ids)).all()
    
    return tasks


@router.get("/{workflow_id}/design")
def read_workflow_design(
    *,
    db: Session = Depends(get_db),
    workflow_id: int,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get workflow design (tasks and dependencies).
    """
    workflow = crud.workflow.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get workflow tasks
    workflow_tasks = db.query(models.WorkflowTask).filter(
        models.WorkflowTask.workflow_id == workflow_id
    ).all()
    
    # Get task dependencies
    dependencies = crud.task_dependency.get_by_workflow(db, workflow_id=workflow_id)
    
    return {
        "tasks": workflow_tasks,
        "dependencies": dependencies
    }


@router.post("/{workflow_id}/design")
def save_workflow_design(
    *,
    db: Session = Depends(get_db),
    workflow_id: int,
    design_data: dict,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Save workflow design (tasks and dependencies).
    """
    workflow = crud.workflow.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Clear existing workflow tasks and dependencies
    db.query(models.WorkflowTask).filter(
        models.WorkflowTask.workflow_id == workflow_id
    ).delete()
    
    db.query(models.TaskDependency).filter(
        models.TaskDependency.workflow_id == workflow_id
    ).delete()
    
    # Save new workflow tasks
    tasks = design_data.get("tasks", [])
    for task_data in tasks:
        workflow_task = models.WorkflowTask(
            workflow_id=workflow_id,
            task_id=task_data["task_id"],
            position_x=task_data.get("position_x", 0),
            position_y=task_data.get("position_y", 0),
            config=task_data.get("config")
        )
        db.add(workflow_task)
    
    # Save new dependencies
    dependencies = design_data.get("dependencies", [])
    for dep_data in dependencies:
        dependency = models.TaskDependency(
            workflow_id=workflow_id,
            source_task_id=dep_data["source_task_id"],
            target_task_id=dep_data["target_task_id"],
            condition=dep_data.get("condition")
        )
        db.add(dependency)
    
    db.commit()
    
    return {"message": "Workflow design saved successfully"}