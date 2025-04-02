import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.database.persistent.config import Base, get_db
from backend.database.persistent.models import User
from backend.api.main import app
from backend.api.dependencies.auth import create_access_token
from backend.utils.password_utils import hash_password
from backend.config.environment import get_environment, Environment

@pytest.fixture(scope="session")
def test_engine():
    """Create a test engine for each test session"""
    if get_environment() == Environment.TESTING:
        DATABASE_URL = f"postgresql://test_user:test_password@localhost:5432/test_db"
        connect_args = {}
    else:
        DATABASE_URL = "sqlite:///./test.db"
        connect_args = {"check_same_thread": False}
    
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    yield engine

@pytest.fixture
def test_db(test_engine):
    """Create a fresh test database for each test"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Create tables
    Base.metadata.drop_all(bind=test_engine)  # Drop all tables first
    Base.metadata.create_all(bind=test_engine)
    
    # Override the dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Return session for test use
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)
        app.dependency_overrides = {}

@pytest.fixture
def client(test_db):
    """Provide a test client with a test database"""
    return TestClient(app)

@pytest.fixture
def test_user(test_db):
    """Create a test user and return it"""
    # First, ensure no user exists with this email
    existing_user = test_db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        test_db.delete(existing_user)
        test_db.commit()
    
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash=hash_password("testpassword"),  # Make sure this matches what you use in tests
        role="USER"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_admin(test_db):
    """Create a test admin user"""
    existing_admin = test_db.query(User).filter(User.email == "admin@example.com").first()
    if existing_admin:
        test_db.delete(existing_admin)
        test_db.commit()
    
    admin = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=hash_password("testpassword"),
        role="ADMIN"
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def auth_headers(test_user):
    """Provide authentication headers for a test user"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    return {"Authorization": f"Bearer {token}"}

def pytest_configure(config):
    """Add custom markers"""
    config.addinivalue_line(
        "markers", "production_settings: marks tests that verify production settings"
    )
