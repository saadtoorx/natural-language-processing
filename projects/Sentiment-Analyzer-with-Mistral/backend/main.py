"""
Sentiment Analyzer API
A FastAPI backend for sentiment analysis using Ollama's Mistral model.
"""

import os
from typing import List, Optional
from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "mistral")

app = FastAPI(
    title="Sentiment Analyzer API",
    description="Analyze text sentiment using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    text: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7


class AnalyzeResponse(BaseModel):
    text: str
    sentiment: str
    success: bool


class BatchAnalyzeRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = None
    temperature: Optional[float] = 0.7


class BatchAnalyzeResponse(BaseModel):
    results: List[AnalyzeResponse]
    total: int
    success_count: int


class HealthResponse(BaseModel):
    api_status: str
    ollama_status: str
    model: str


def analyze_text(text: str, model: str = None, temperature: float = 0.7) -> dict:
    """
    Analyze sentiment of a single text using Ollama.
    Returns dict with text, sentiment, and success status.
    """
    model = model or DEFAULT_MODEL
    
    prompt = (
        "What is the sentiment of this text? "
        "Respond with ONLY one word: Positive, Negative, or Neutral.\n\n"
        f"Text: {text}"
    )
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        sentiment = result.get("response", "").strip()
        
        # Clean up the response to get just the sentiment word
        sentiment_lower = sentiment.lower()
        if "positive" in sentiment_lower:
            sentiment = "Positive"
        elif "negative" in sentiment_lower:
            sentiment = "Negative"
        elif "neutral" in sentiment_lower:
            sentiment = "Neutral"
        
        return {"text": text, "sentiment": sentiment, "success": True}
    
    except requests.exceptions.ConnectionError:
        return {"text": text, "sentiment": "Error: Cannot connect to Ollama", "success": False}
    except requests.exceptions.Timeout:
        return {"text": text, "sentiment": "Error: Request timed out", "success": False}
    except Exception as e:
        return {"text": text, "sentiment": f"Error: {str(e)}", "success": False}


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Check if the API and Ollama are running."""
    ollama_status = "offline"
    
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            ollama_status = "online"
    except:
        ollama_status = "offline"
    
    return {
        "api_status": "online",
        "ollama_status": ollama_status,
        "model": DEFAULT_MODEL
    }


@app.post("/analyze/", response_model=AnalyzeResponse)
def analyze_sentiment(text: str = Form(...)):
    """Analyze sentiment of a single text (form data)."""
    result = analyze_text(text)
    return result


@app.post("/analyze/json", response_model=AnalyzeResponse)
def analyze_sentiment_json(request: AnalyzeRequest):
    """Analyze sentiment of a single text (JSON body)."""
    result = analyze_text(request.text, request.model, request.temperature)
    return result


@app.post("/analyze/batch", response_model=BatchAnalyzeResponse)
def analyze_batch(request: BatchAnalyzeRequest):
    """Analyze sentiment of multiple texts."""
    results = []
    success_count = 0
    
    for text in request.texts:
        result = analyze_text(text, request.model, request.temperature)
        results.append(result)
        if result["success"]:
            success_count += 1
    
    return {
        "results": results,
        "total": len(request.texts),
        "success_count": success_count
    }