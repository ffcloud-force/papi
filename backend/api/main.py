from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import cases, users, auth, chat
from backend.database.persistent.seed import Seeder
from backend.services.database_service import DatabaseService
from backend.handler.database.database_handler import DatabaseHandler
from backend.database.persistent.config import get_db
import uvicorn


# Create admin user if no users exist – for development purposes
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_admin_if_needed()
    await create_prompts_if_needed()
    yield
    print("App is shutting down")


async def create_prompts_if_needed():
    """Check if any prompts exist in the DB, if not create the default prompts"""
    db = next(get_db())
    db_handler = DatabaseHandler(db)
    db_service = DatabaseService(db_handler)
    seeder = Seeder(db_service)
    seeder.seed_prompts()


async def create_admin_if_needed():
    """Check if any users exist in the DB, if not create the admin user"""
    db = next(get_db())
    db_handler = DatabaseHandler(db)
    db_service = DatabaseService(db_handler)
    seeder = Seeder(db_service)
    seeder.seed_users()


app = FastAPI(
    title="PAPI BOT API",
    description="API for the PAPI BOT",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(cases.router, prefix="/cases", tags=["Cases"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/")
def read_root():
    return {"message": "Wilkommen bei der PAPI BOT API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
