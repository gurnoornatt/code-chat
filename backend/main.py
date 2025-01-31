from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from dotenv import load_dotenv
import os
from backend.routes import auth, chat, files, resources

# Load environment variables
load_dotenv()

# Initialize Sentry only if DSN is provided and valid
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn and sentry_dsn.startswith(("http://", "https://")):
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,
        )
    except Exception as e:
        print(f"Failed to initialize Sentry: {e}")

app = FastAPI(
    title="AI Tutor API",
    description="Backend API for AI Tutor application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(files.router)
app.include_router(resources.router)

@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status"""
    return {"status": "healthy", "message": "API is running"} 