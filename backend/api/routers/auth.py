from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from argon2.exceptions import VerifyMismatchError
from datetime import datetime
from backend.database.persistent.config import get_db
from backend.database.persistent.models import User
from backend.api.schemas.auth import LoginResponse, Token
from backend.api.schemas.user import UserResponse
from backend.api.dependencies.auth import get_current_user, create_access_token, verify_password

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    try:
        verify_password(form_data.password, user.password_hash)
    except VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login date
    user.last_login_date = datetime.now()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    # Use Pydantic models for response
    return LoginResponse(
        id=user.id,
        registration_date=user.registration_date,
        last_login_date=user.last_login_date,
        token=Token(
            access_token=access_token,
            token_type="bearer"
        )
    )

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    # Convert SQL model to Pydantic model
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        registration_date=current_user.registration_date,
        last_login_date=current_user.last_login_date
    )

