from app.db.session import engine
from app import models
from sqlalchemy.orm import Session

with Session(engine) as db:
    users = db.query(models.User).all()
    print('Users in database:')
    for u in users:
        print(f'- {u.username} ({u.email})')