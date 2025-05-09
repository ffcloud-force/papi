from enum import Enum
from typing import Callable, Annotated
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone
from backend.database.persistent.models import User
from backend.api.dependencies.database import database_service_dependency
import inspect
from backend.config.settings import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(
    db_service: database_service_dependency,
    token: str = Depends(oauth2_scheme)
): 
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
        
    user = db_service.get_user_by_email(email)
    if user is None:
        raise credentials_exception
        
    return user

current_user_dependency = Annotated[User, Depends(get_current_user)]


def create_access_token(
        data: dict, 
        expires_delta: timedelta = None
):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

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
    current_user: current_user_dependency
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
    param_name = {
        ResourceType.CASE: "case_id",
        ResourceType.USER: "user_id",
        # Add other resource types as needed
    }[resource_type]

    def check_access(
        current_user: current_user_dependency,
        db_service: database_service_dependency,
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
            case = db_service.get_case_by_id(resource_id)
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
    
    # Update the signature to use db_service instead of db
    check_access.__signature__ = inspect.signature(check_access).replace(
        parameters=[
            inspect.Parameter(
                param_name,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str
            ),
            *[p for p in inspect.signature(check_access).parameters.values()
              if p.name in ('db_service', 'current_user')]
        ]
    )
    
    return check_access

current_user_resource_access_dependency = Annotated[User, Depends(require_resource_access(ResourceType.USER))]