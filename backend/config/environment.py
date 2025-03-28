import os
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

def get_environment() -> Environment:
    """Get the current environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    return Environment(env)

def is_production() -> bool:
    """Check if we're running in production."""
    return get_environment() == Environment.PRODUCTION

def is_testing() -> bool:
    """Check if we're running in test mode."""
    return get_environment() == Environment.TESTING
