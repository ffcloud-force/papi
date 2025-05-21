import os

# import asyncio
from sqlalchemy import create_engine

# from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Determine if we're in production or development
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Set up database URL based on environment
if ENVIRONMENT == "production":
    # Use PostgreSQL in production (cloud)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "papi")

    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # PostgreSQL-specific connection arguments
    connect_args = {}
else:
    # Use SQLite in development (local)
    DATABASE_URL = "sqlite:///./papi.db"

    # SQLite-specific connection arguments
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)
# async_engine = create_async_engine(DATABASE_URL, connect_args=connect_args)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
