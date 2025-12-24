from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from fastapi.responses import HTMLResponse, JSONResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from pydantic import BaseModel, Field

import os


# FastAPI() 객체 생성
app = FastAPI()

abs_path= os.path.dirname(os.path.realpath(__file__))
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더를 app에 연결
app.mount('/static', StaticFiles(directory=f"{abs_path}/static"), name="static")

#############################################################
# llm과 관련된 사전 작업
# api key 환경변수 설정
# API key 로딩
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

# llm 객체생성
llm = ChatOpenAI(model="gpt-5-nano", temperature=0.7)

# json parser로 응답 리턴

# BaseModel 상속받기
class JobDescription(BaseModel):
    job_role: str = Field(description = '직군명')
    level: str = Field(description = '숙련도 수준')
    core_skills: str = Field(description = '핵심 기술 역량')
    tools: str = Field(description = '팔수 도구 및 기술 스택')
    soft_skills: str = Field(description = '비기술 역량')
    description: str = Field(description = '직군 설명')

parser = JsonOutputParser(pydantic_object=JobDescription)

# 프롬프트 만들기
prompt_template = PromptTemplate(
    template = """
    당신은 취업 컨설턴트입니다.
    최신 정보를 반영한 직군에 대한 설명을 작성해주세요.
    \n{format_instructions}\n{job_role}, {level}\n
    """,
    input_variables=['job_role', 'level'],
    partial_variables={'format_instructions': parser.get_format_instructions()},
)

# chain 객체 만들기
chain = prompt_template | llm | parser
#############################################################

@app.get("/")
def home(request: Request):
    test = 100
    return templates.TemplateResponse("index.html", {"request": request, "test": test})

# llm 질문,응답 받고, 결과를 리턴
@app.post("/generate")
def generate(request: Request, job_role: str = Form(...), level: str = Form(...)):
    # llm에 질문한(클라이언트에서 넘어온) 키워드를 받음
    # gpt에 질문하고 응답받기
    input_data = {"job_role": job_role, "level": level}
    print("llm 요청시작")
    response = chain.invoke(input_data)
    print("llm 요청완료")
    print(response)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "result": response})