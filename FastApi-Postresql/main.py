from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
import models
from database import sessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class ChoiceBase(BaseModel):
    choice_txt:str
    is_correct:bool
    
class QuestionBase(BaseModel):
    question_txt: str
    choices: List[ChoiceBase]
    
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Quiz Game API!"}

@app.get("/questions/{question_id}")
async def read_questions(question_id:int, db:db_dependency):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail = "question not found")
    return result

@app.get("/choices/{question_id}")
async def read_choices(question_id:int, db:db_dependency):
    result = db.query(models.Choice).filter(models.Choice.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail="Choices not found")
    return result

@app.post("/questions/")
async def create_question(questions:QuestionBase, db:db_dependency):
    db_question = models.Questions(question_text = questions.question_txt)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in questions.choices:
        db_choice = models.Choice(choice_text = choice.choice_txt, is_correct = choice.is_correct, question_id = db_question.id)
        db.add(db_choice)
    db.commit()
    return {"status": "success"}
        
