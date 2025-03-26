import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# JWT Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.urandom(32).hex()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Argon2 Settings
ARGON2_TIME_COST = int(os.getenv("ARGON2_TIME_COST", 3))
ARGON2_MEMORY_COST = int(os.getenv("ARGON2_MEMORY_COST", 100000))
ARGON2_PARALLELISM = int(os.getenv("ARGON2_PARALLELISM", 4))
ARGON2_HASH_LENGTH = int(os.getenv("ARGON2_HASH_LENGTH", 32))
ARGON2_SALT_LENGTH = int(os.getenv("ARGON2_SALT_LENGTH", 20)) 