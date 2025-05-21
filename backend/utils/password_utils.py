from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from backend.config.settings import (
    ARGON2_TIME_COST,
    ARGON2_MEMORY_COST,
    ARGON2_PARALLELISM,
    ARGON2_HASH_LENGTH,
    ARGON2_SALT_LENGTH,
)

# Password hasher setup
ph = PasswordHasher(
    time_cost=ARGON2_TIME_COST,
    memory_cost=ARGON2_MEMORY_COST,
    parallelism=ARGON2_PARALLELISM,
    hash_len=ARGON2_HASH_LENGTH,
    salt_len=ARGON2_SALT_LENGTH,
)


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except VerifyMismatchError:
        return False
    except Exception as e:
        raise e
