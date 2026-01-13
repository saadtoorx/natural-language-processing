from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from pypdf import PdfReader
from langdetect import detect
import io

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", 10000))
MIN_TEXT_LENGTH = int(os.getenv("MIN_TEXT_LENGTH", 10))

# Initialize FastAPI app
app = FastAPI(
    title="LLaMA Text Summarizer API",
    description="A production-ready API for text summarization using local LLaMA model via Ollama",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class SummaryResponse(BaseModel):
    summary: str
    mode: str
    language: str
    original_length: int
    summary_length: int

class HealthResponse(BaseModel):
    status: str
    ollama_status: str

# Prompt templates for different modes
PROMPTS = {
    "brief": "Summarize this text in 2-3 sentences:\n\n{text}",
    "detailed": "Provide a comprehensive summary of this text, covering all main points:\n\n{text}",
    "bullets": "Summarize this text as bullet points (use - for each point):\n\n{text}"
}

LANGUAGE_PROMPTS = {
    "en": "",
    "es": "Respond in Spanish. ",
    "fr": "Respond in French. ",
    "de": "Respond in German. ",
    "it": "Respond in Italian. ",
    "pt": "Respond in Portuguese. ",
    "zh-cn": "Respond in Chinese. ",
    "zh-tw": "Respond in Chinese. ",
    "ja": "Respond in Japanese. ",
    "ko": "Respond in Korean. ",
    "ar": "Respond in Arabic. ",
    "hi": "Respond in Hindi. ",
    "ur": "Respond in Urdu. ",
}


def get_language_instruction(lang_code: str) -> str:
    """Get language instruction for the prompt."""
    return LANGUAGE_PROMPTS.get(lang_code, f"Respond in the same language as the input text. ")


def call_ollama(prompt: str) -> str:
    """Make a request to Ollama API."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Please ensure Ollama is running on your machine."
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Ollama request timed out. The text might be too long."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Ollama: {str(e)}"
        )


def validate_text(text: str) -> None:
    """Validate input text length."""
    if len(text.strip()) < MIN_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text is too short. Minimum {MIN_TEXT_LENGTH} characters required."
        )
    if len(text) > MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Text is too long. Maximum {MAX_TEXT_LENGTH} characters allowed."
        )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API and Ollama health status."""
    ollama_status = "unknown"
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        ollama_status = "healthy" if response.ok else "unhealthy"
    except:
        ollama_status = "unreachable"
    
    return HealthResponse(
        status="healthy",
        ollama_status=ollama_status
    )


@app.post("/summarize/", response_model=SummaryResponse)
async def summarize(
    text: str = Form(...),
    mode: str = Form("brief")
):
    """
    Summarize the provided text.
    
    - **text**: The text to summarize
    - **mode**: Summarization mode - 'brief', 'detailed', or 'bullets'
    """
    # Validate input
    validate_text(text)
    
    if mode not in PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Choose from: {', '.join(PROMPTS.keys())}"
        )
    
    # Detect language
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "en"
    
    # Build prompt
    lang_instruction = get_language_instruction(detected_lang)
    prompt = lang_instruction + PROMPTS[mode].format(text=text)
    
    # Get summary from Ollama
    summary = call_ollama(prompt)
    
    return SummaryResponse(
        summary=summary.strip(),
        mode=mode,
        language=detected_lang,
        original_length=len(text),
        summary_length=len(summary.strip())
    )


@app.post("/summarize/pdf/", response_model=SummaryResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    mode: str = Form("brief")
):
    """
    Extract text from a PDF and summarize it.
    
    - **file**: PDF file to summarize
    - **mode**: Summarization mode - 'brief', 'detailed', or 'bullets'
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    
    # Read PDF content
    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read PDF: {str(e)}"
        )
    
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from PDF. The file might be scanned or image-based."
        )
    
    # Validate and summarize
    validate_text(text)
    
    if mode not in PROMPTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode. Choose from: {', '.join(PROMPTS.keys())}"
        )
    
    # Detect language
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "en"
    
    # Build prompt
    lang_instruction = get_language_instruction(detected_lang)
    prompt = lang_instruction + PROMPTS[mode].format(text=text)
    
    # Get summary
    summary = call_ollama(prompt)
    
    return SummaryResponse(
        summary=summary.strip(),
        mode=mode,
        language=detected_lang,
        original_length=len(text),
        summary_length=len(summary.strip())
    )