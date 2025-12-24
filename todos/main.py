from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import os

# database 파일로부터 engine, SessionLocal, Base import
# Base가 여러군데에 있기 때문에 models에서 가져오라고 명시해야 DBeaver에 테이블 생성됨
from database import engine, SessionLocal
from models import Base
import models
# 연결한 DB엔진에 테이블 생성
# models에 정의한 모든 클래스를 테이블로 생성
Base.metadata.create_all(bind=engine)

# FastAPI() 객체 생성
app = FastAPI()

abs_path = os.path.dirname(os.path.realpath(__file__))
# print(abs_path)
# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
# app.mount("/static", StaticFiles(directory=f"static"), name="static")
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")

# DB 세션 객체 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db  # 세선 작업이 끝날때까지 대기
    finally:
        # 마지막에 무조건 닫아야함
        db.close()

@app.get("/")
def home(request: Request,
            db : Session = Depends(get_db)):
    # todo 데이터 조회
    todos = db.query(models.Todo).order_by(models.Todo.id.desc()).all()
    # print(todos)
    # for todo in todos:
    #     print(todo.id, todo.task, todo.completed)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": todos})

@app.post('/add')
def home(request: Request,
         task: str = Form(...),
         db: Session = Depends(get_db)):
    # todo 객체 생성
    todo = models.Todo(task=task)
    print(todo)
    # todo를 db 추가
    db.add(todo)
    # db 커밋(db에 반영)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"),
                            status_code=status.HTTP_303_SEE_OTHER)