import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.persistent.models import User
from backend.database.persistent.config import get_db
from backend.api.schemas.user import UserCreate, UserUpdate, UserDelete, UserResponse
from backend.api.dependencies.auth import hash_password, verify_password, admin_only, check_user_access
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    _: User = Depends(lambda: check_user_access(user_id)),
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
    _: User = Depends(admin_only),  # Admin-only endpoint
    db: Session = Depends(get_db)
):
    return db.query(User).all()

@router.post("/")
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    #check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Ein Nutzer mit dieser E-Mail-Adresse existiert bereits.")

    #hash the password with the salt
    hashed_password = hash_password(user.password)

    #create new user
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

    #@TODO: send email to user to validate email
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(lambda: check_user_access(user_id)),
    db: Session = Depends(get_db)
):
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

    try:
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Email bereits registriert"
        )

    # Return updated user data
    return UserResponse.from_orm(current_user)
    

@router.delete("/{user_id}")
async def delete_user(
    user_id: str, 
    _: User = Depends(lambda: check_user_access(user_id)),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(existing_user)
    db.commit()