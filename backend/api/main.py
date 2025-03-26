from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routers import cases, users, auth, chat
import uvicorn

app = FastAPI(
    title="PAPI BOT API",
    description="API for the PAPI BOT",
    version="0.1.0",
    docs_url="/docs"  # This is the default but just to be explicit
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
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
