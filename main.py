from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm.session import Session

from database import models
from database.db import engine, SessionLocal
from services import isemail
from security import router as security_router
from security.hashing import get_password_hash
from routers import router

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(security_router.router)


@app.on_event('startup')
def startup():
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    roles = [role.title for role in db.query(models.Role).all()]
    if not roles:
        a = models.Role(title='Admin')
        u = models.Role(title='User')
        db.add_all([a, u])

    if 'admin' not in [user.username for user in db.query(models.User).all()]:
        # while not isemail(admin_email := input('Choose admin\'s email: ')):
        #     print('Wrong email!')
        # admin_password = get_password_hash(input('Choose admin\'s password: '))
        admin_email = 'admin@observers.com'
        admin_password = get_password_hash('admin')
        admin = models.User(
            username='admin',
            email=admin_email,
            password=admin_password,
            role_id=1
        )
        db.add(admin)

    db.commit()
