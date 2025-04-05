from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from argon2.exceptions import VerifyMismatchError
from backend.database.persistent.models import User
from backend.api.schemas.user import UserResponse
from backend.api.dependencies.auth import get_current_user, create_access_token
from backend.utils.password_utils import verify_password
from backend.services.database_service import DatabaseService
from backend.api.dependencies.database import get_database_service

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get access token for authentication.
    
    - **username**: Your email address
    - **password**: Your password
    - Note: Client ID and Secret are not required
    """
    # Find user by email
    user = db_service.get_user_by_email(form_data.username)
    
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
    db_service.update_user_last_login(user.id)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):

    # Convert SQL model to Pydantic model
    return UserResponse(
        id=current_user.id,
        role=current_user.role,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        registration_date=current_user.registration_date,
        last_login_date=current_user.last_login_date
    )

