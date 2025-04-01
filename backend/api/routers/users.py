from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.persistent.models import User
from backend.database.persistent.config import get_db
from backend.api.schemas.user import UserCreate, UserUpdate, UserDelete, UserResponse
from backend.api.dependencies.auth import require_resource_access, admin_only, check_user_access, ResourceType
from backend.utils.password_utils import hash_password, verify_password
from sqlalchemy.exc import IntegrityError
from backend.services.database_service import DatabaseService
from backend.api.dependencies.database_service import get_database_service

router = APIRouter()

current_user_resource_access_dependency = Annotated[User, Depends(require_resource_access(ResourceType.USER))]
user_service_dependency = Annotated[DatabaseService, Depends(get_database_service)]

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    # _: User = Depends(admin_only), # @TODO: REMOVE BEFORE PRODUCTION
    db: Session = Depends(get_db)
):
    """
    Admin only endpoint, normal users use the /me endpoint
    """
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="Der angegebene Nutzer wurde nicht gefunden.")
    return UserResponse.model_validate(user)

@router.get("/")
async def list_users(
    # _: User = Depends(admin_only),  # @TODO: REMOVE BEFORE PRODUCTION
    db: Session = Depends(get_db)
):
    return db.query(User).all()

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db_service: DatabaseService = Depends(get_database_service)
):
    try:
        new_user = db_service.create_user(user)
        return UserResponse.model_validate(new_user)
    except ValueError as e:
        raise HTTPException(
            status_code=400, 
            detail="Ein Nutzer mit dieser E-Mail-Adresse existiert bereits."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Ein Fehler ist aufgetreten"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: current_user_resource_access_dependency,
    db_service: user_service_dependency
):
    #@TODO: NEEDS WORK, NOT A PRIO
    # If updating sensitive fields (email/password), require current password
    if user_update.email or user_update.password:
        if not user_update.current_password:
            raise HTTPException(
                status_code=400,
                detail="Aktuelles Passwort ist erforderlich, um E-Mail oder Passwort zu aktualisieren"
            )
        
        # Verify current password
        try:
            verify_password(user_update.current_password, current_user.password_hash)
        except:
            raise HTTPException(
                status_code=401,
                detail="Aktuelles Passwort ist falsch"
            )

    # Update user fields that were provided
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Remove current_password from update data
    update_data.pop('current_password', None)
    
    # Hash new password if provided
    if 'password' in update_data:
        update_data['password_hash'] = hash_password(update_data.pop('password'))

    # Update user in database
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db_service.update_user(current_user.id, update_data)

    # Return updated user data
    return UserResponse.from_orm(current_user)
    

@router.delete("/{user_id}")
async def delete_user(
    current_user: User = Depends(require_resource_access(ResourceType.USER)),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.id == current_user.id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(existing_user)
    db.commit()