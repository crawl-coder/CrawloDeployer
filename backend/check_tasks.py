from app.db.session import engine
from app import models
from sqlalchemy.orm import Session

with Session(engine) as db:
    tasks = db.query(models.Task).all()
    print('Tasks:')
    for t in tasks:
        print(f'- Task {t.id}: distribution_mode={t.distribution_mode}')