from argon2 import PasswordHasher

#argon2 hasher
ph = PasswordHasher(
    time_cost=3,
    memory_cost=100000,
    parallelism=4,
    hash_len=32,
    salt_len=20,
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password, password)
    except Exception as e:
        return False