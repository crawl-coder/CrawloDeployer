from app.db.session import engine
from app import models
from sqlalchemy.orm import Session

# 导入TaskDistributionMode枚举
from app.models.task import TaskDistributionMode

with Session(engine) as db:
    tasks = db.query(models.Task).all()
    print('Tasks before fix:')
    for t in tasks:
        print(f'- Task {t.id}: distribution_mode={t.distribution_mode}')
        
    # 更新所有distribution_mode为None的任务
    for t in tasks:
        if t.distribution_mode is None:
            t.distribution_mode = TaskDistributionMode.ANY
            print(f'Fixed Task {t.id}: set distribution_mode to ANY')
            
    db.commit()
    
    # 验证修复结果
    tasks = db.query(models.Task).all()
    print('\nTasks after fix:')
    for t in tasks:
        print(f'- Task {t.id}: distribution_mode={t.distribution_mode}')