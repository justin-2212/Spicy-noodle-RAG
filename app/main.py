import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.utils.logger import logger

# Set up FastAPI app
app = FastAPI(
    title="Spicy Noodle RAG Chatbot",
    description="Intelligent assistant for Spicy Noodle Restaurant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api")

# Mount static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_path):
    os.makedirs(static_path)
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the chat interface."""
    index_file = os.path.join(static_path, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Chatbot UI coming soon...</h1>")

@app.on_event("startup")
async def startup_event():
    logger.info("Chatbot API is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Chatbot API is shutting down...")
