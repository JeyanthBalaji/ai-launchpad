"""
AI Launchpad — FastAPI backend.

Exposes POST /generate which runs the agent crew and returns a full
startup kit (name, landing-page copy, brand, social captions).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import run_crew, MOCK_MODE

app = FastAPI(title="AI Launchpad API", version="0.1.0")

# Allow the Vite dev server (and the built frontend) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production if you like
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    idea: str
    audience: str = "general"


@app.get("/")
def root():
    return {"status": "ok", "service": "AI Launchpad API", "mock_mode": MOCK_MODE}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    """Turn one idea into a full startup kit."""
    result = await run_crew(req.idea.strip(), req.audience.strip())
    return result
