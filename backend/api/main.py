from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import users, documents, auth

app = FastAPI(title="PAPI API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
# app.include_router(documents.router, prefix="/documents", tags=["Documents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to PAPI API"}
