from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.models import User
from backend.database.config import get_db
from backend.api.schemas import UserCreate, UserUpdate, UserResponse
from argon2 import PasswordHasher
import uuid
from backend.api.routers.utils import hash_password

router = APIRouter()

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
    
@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    #hash the password with the salt
    hashed_password = hash_password(user.password)

    new_user = User(
        id=str(uuid.uuid4()),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user