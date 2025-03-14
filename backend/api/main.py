from fastapi import FastAPI
from backend.api.routers import users, documents, auth

app = FastAPI(title="PAPI API")

# Include routers
# app.include_router(auth.router, tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(documents.router, prefix="/documents", tags=["Documents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to PAPI API"}
