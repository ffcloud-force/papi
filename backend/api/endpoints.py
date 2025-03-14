from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database.config import get_db
from .database.models import User, Document
from . import schemas  # Pydantic models for request/response validation

app = FastAPI()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email, hashed_password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/documents/", response_model=schemas.Document)
def create_document(user_id: int, document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    db_document = Document(**document.dict(), owner_id=user_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

# Add more endpoints for updating, deleting, etc.
