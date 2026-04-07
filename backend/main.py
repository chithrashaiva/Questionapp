from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from typing import List, Optional

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./quiz.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Database Models
class QuestionModel(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String)
    options = Column(String)  # Stored as comma-separated string
    answer = Column(String)

class ScoreModel(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    score = Column(Integer)
    total = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class QuestionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question: str
    options: List[str]

class AnswerSubmit(BaseModel):
    question_id: int
    answer: str

class FinalScoreSubmit(BaseModel):
    username: str
    score: int
    total: int

class LeaderboardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    username: str
    score: int
    total: int

# Initialize questions if DB is empty
def init_db():
    db = SessionLocal()
    try:
        if db.query(QuestionModel).count() == 0:
            initial_questions = [
                {"question": "What does HTML stand for?", "options": "Hyper Text Markup Language,Home Tool Markup Language,Hyperlinks and Text Markup Language,Hyper Tool Markup Language", "answer": "Hyper Text Markup Language"},
                {"question": "Which programming language is known as the language of the web?", "options": "Python,C++,JavaScript,Java", "answer": "JavaScript"},
                {"question": "What is React primarily used for?", "options": "Building databases,Building user interfaces,Routing,Styling documents", "answer": "Building user interfaces"},
                {"question": "Which of the following is a CSS framework?", "options": "Django,Express,TailwindCSS,FastAPI", "answer": "TailwindCSS"},
                {"question": "Which HTTP method is typically used to retrieve data from an API?", "options": "POST,PUT,GET,DELETE", "answer": "GET"}
            ]
            for q in initial_questions:
                db.add(QuestionModel(**q))
            db.commit()
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        db.close()

init_db()

@app.get("/questions", response_model=List[QuestionSchema])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(QuestionModel).all()
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "question": q.question,
            "options": q.options.split(",") if q.options else []
        })
    return result

@app.post("/submit")
def submit_answer(submission: AnswerSubmit, db: Session = Depends(get_db)):
    q = db.query(QuestionModel).filter(QuestionModel.id == submission.question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = (q.answer == submission.answer)
    return {"correct": is_correct, "correct_answer": q.answer if not is_correct else None}

@app.post("/submit-score")
def submit_score(score_data: FinalScoreSubmit, db: Session = Depends(get_db)):
    new_score = ScoreModel(username=score_data.username, score=score_data.score, total=score_data.total)
    db.add(new_score)
    db.commit()
    return {"message": "Score saved successfully"}

@app.get("/leaderboard", response_model=List[LeaderboardSchema])
def get_leaderboard(db: Session = Depends(get_db)):
    scores = db.query(ScoreModel).order_by(ScoreModel.score.desc()).limit(10).all()
    return scores