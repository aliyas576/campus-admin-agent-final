from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from backend.models.database import init_db
from backend.api import chat, students, analytics
from contextlib import asynccontextmanager

init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    init_db()
    
    yield
    
    # Shutdown - clean up resources
    print("Shutting down...")
    # Add any cleanup logic here

app = FastAPI(
    title="Campus Admin Agent API",
    description="AI-powered campus administration assistant",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(students.router)
app.include_router(analytics.router)

@app.get("/")
async def root():
    return {
        "message": "Campus Admin Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "chat_stream": "/chat/stream",
            "students": "/students",
            "analytics": "/analytics"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)