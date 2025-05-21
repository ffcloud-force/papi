import os
import secrets
from dotenv import load_dotenv
from backend.config.environment import get_environment, Environment

load_dotenv()  # Load environment variables from .env file

# Generate a secret key only if one doesn't exist in environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "development_secret_key")
if not JWT_SECRET_KEY:
    # Generate it once and tell the developer to save it
    generated_key = secrets.token_hex(32)
    print(f"""
    WARNING: No JWT_SECRET_KEY found in environment variables.
    Generated new key: {generated_key}
    
    Please add this to your .env file:
    JWT_SECRET_KEY={generated_key}
    """)
    JWT_SECRET_KEY = generated_key

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = (
    30 if get_environment() == Environment.PRODUCTION else 60 * 24
)

# Argon2 Settings
if get_environment() == Environment.PRODUCTION:
    ARGON2_TIME_COST = 4
    ARGON2_MEMORY_COST = 100000
else:
    ARGON2_TIME_COST = 2
    ARGON2_MEMORY_COST = 10000

ARGON2_PARALLELISM = 1
ARGON2_HASH_LENGTH = 32
ARGON2_SALT_LENGTH = 16
