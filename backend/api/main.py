from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import cases, users, auth, chat
import uvicorn
import uuid
import os
from backend.database.persistent.config import SessionLocal
from backend.database.persistent.models import User, UserRole
from backend.api.dependencies.auth import hash_password

app = FastAPI(
    title="PAPI BOT API",
    description="API for the PAPI BOT",
    version="0.1.0",
    docs_url="/docs"  # This is the default but just to be explicit
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Create admin user if no users exist – for development purposes
@app.on_event("startup")
async def create_admin_if_needed():
    """Check if any users exist in the DB, if not create an admin user"""
    db = SessionLocal()
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        if user_count == 0:
            # Generate a secure random password
            password = os.getenv("ADMIN_PASSWORD")
            # Create admin user
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@papi.com",
                first_name="Papa",
                last_name="Smurf",
                password_hash=hash_password(password),
                role=UserRole.ADMIN
            )
            db.add(admin)
            db.commit()
            
            # Print credentials to console for developer
            print("\n" + "="*50)
            print(" ADMIN USER CREATED - SAVE THESE CREDENTIALS")
            print("="*50)
            print(f" Email: {admin.email}")
            print(f" Password: {password}")
            print("="*50 + "\n")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Wilkommen bei der PAPI BOT API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
