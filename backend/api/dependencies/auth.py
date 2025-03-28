from enum import Enum
from typing import Optional, Callable, Literal
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Path
from datetime import datetime, timedelta, timezone
from backend.database.persistent.config import get_db
from backend.database.persistent.models import User, Case
from backend.config.settings import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LENGTH,
    ARGON2_SALT_LENGTH
)
from functools import partial
import inspect

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Password hasher setup
ph = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LENGTH,
    salt_len=ARGON2_SALT_LENGTH,
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except Exception as e:
        raise VerifyMismatchError("Password mismatch")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user

def admin_only(current_user: User = Depends(get_current_user)):
    """Check if the current user is an admin"""
    if not current_user.role.is_admin():
        raise HTTPException(
            status_code=403, 
            detail="Admin privileges required"
        )
    return current_user

def check_user_access(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Check if current user can access the specified user"""
    if not current_user.role.can_access_resource(user_id, current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="Du bist nicht berechtigt, diese Aktion auszuführen."
        )
    return current_user

class ResourceType(Enum):
    USER = "user"
    CASE = "case"
    QUESTION = "question"
    # Add other resource types as needed

def require_resource_access(resource_type: ResourceType) -> Callable:
    """
    Factory function that creates a dependency for checking resource access.
    """
    # Define the parameter name based on resource type
    param_name = {
        ResourceType.CASE: "case_id",
        ResourceType.USER: "user_id",
        # Add other resource types as needed
    }[resource_type]

    def check_access(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        **path_params  # This will receive all path parameters
    ) -> User:
        # Get the ID from the correct path parameter
        resource_id = path_params[param_name]

        # Admins can access everything
        if current_user.role.is_admin():
            return current_user

        # Get resource owner ID based on type
        owner_id = None
        if resource_type == ResourceType.USER:
            owner_id = resource_id
        elif resource_type == ResourceType.CASE:
            case = db.query(Case).filter(Case.id == resource_id).first()
            if not case:
                raise HTTPException(status_code=404, detail=f"{resource_type.value} not found")
            owner_id = case.user_id

        # Use existing role-based access check
        if not current_user.role.can_access_resource(owner_id, current_user.id):
            raise HTTPException(
                status_code=403,
                detail="Du bist nicht berechtigt, diese Aktion auszuführen."
            )
            
        return current_user
    
    # Set the dependency's signature to match the route parameter
    check_access.__signature__ = inspect.signature(check_access).replace(
        parameters=[
            inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str
            ),
            *[p for p in inspect.signature(check_access).parameters.values()
              if p.name in ('db', 'current_user')]
        ]
    )
    
    return check_access