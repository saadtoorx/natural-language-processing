from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Metadata
app = FastAPI(
    title="Product Review Analyzer API",
    description="""
## Product Review Analyzer API

A powerful API for analyzing product reviews using AI (Ollama/Mistral).

### Features:
- **Sentiment Analysis**: Classify reviews as Positive, Negative, or Neutral
- **Topic Extraction**: Identify main discussion topics
- **Summarization**: Generate concise review summaries
- **Batch Processing**: Analyze multiple reviews at once

### Requirements:
- Ollama running locally with Mistral model
- `ollama pull mistral` to download the model
    """,
    version="2.0.0",
    contact={
        "name": "Product Review Analyzer",
        "url": "https://github.com/yourusername/product-review-analyzer",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# ============== Input Models ==============

class ReviewRequest(BaseModel):
    """Request model for single review analysis."""
    text: str = Field(
        ...,
        min_length=3,
        max_length=5000,
        description="The review text to analyze",
        examples=["The battery life is amazing but the screen is too dim."]
    )
    product_name: str = Field(
        default="Product",
        max_length=100,
        description="Name of the product being reviewed",
        examples=["iPhone 15", "AirPods Pro"]
    )

class ReviewItem(BaseModel):
    """Individual review item for batch processing."""
    text: str = Field(..., min_length=3, max_length=5000)
    product_name: str = Field(default="Product", max_length=100)

class BatchReviewRequest(BaseModel):
    """Request model for batch review analysis."""
    reviews: List[ReviewItem] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of reviews to analyze (max 100)"
    )

# ============== Output Models ==============

class AnalysisResponse(BaseModel):
    """Response model for single review analysis."""
    sentiment: str = Field(..., description="Sentiment classification: Positive, Negative, or Neutral")
    topic: str = Field(..., description="Main topic of the review (1-3 words)")
    summary: str = Field(..., description="Concise summary of the review")

class BatchResultItem(BaseModel):
    """Individual result in batch analysis."""
    review: str
    product_name: str
    sentiment: str
    topic: str
    summary: str
    error: Optional[str] = None

class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis."""
    results: List[BatchResultItem]
    total_count: int
    success_count: int
    error_count: int

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    version: str
    ollama_status: str

# ============== CORS Middleware ==============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Configuration ==============

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"
REQUEST_TIMEOUT = 120.0

# ============== Helper Functions ==============

async def check_ollama_status() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            return response.status_code == 200
    except:
        return False

async def query_ollama(prompt: str) -> str:
    """
    Helper function to query Ollama asynchronously.
    
    Args:
        prompt: The prompt to send to the model
        
    Returns:
        The model's response text
        
    Raises:
        HTTPException: If connection fails or other errors occur
    """
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
    except httpx.TimeoutException:
        logger.error("Ollama request timed out")
        raise HTTPException(status_code=504, detail="Request timed out. The model is taking too long to respond.")
    except httpx.ConnectError:
        logger.error("Could not connect to Ollama")
        raise HTTPException(status_code=503, detail="Could not connect to Ollama. Make sure it's running on localhost:11434")
    except httpx.RequestError as e:
        logger.error(f"Ollama connection error: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable: Could not connect to Ollama.")
    except Exception as e:
        logger.error(f"Error querying Ollama: {e}")
        return "Error"

def create_sentiment_prompt(text: str, product: str) -> str:
    """Create prompt for sentiment analysis."""
    return (
        f"Analyze the sentiment of this review for the {product}.\n"
        "Rules:\n"
        "- Return 'Positive' if the review is mostly happy or praising.\n"
        "- Return 'Negative' if the review is mostly unhappy or complaining.\n"
        "- Return 'Neutral' if the review mentions BOTH pros and cons (mixed), or is indifferent.\n"
        f"Review: {text}\n\n"
        "Answer with ONE word: Positive, Negative, or Neutral."
    )

def create_topic_prompt(text: str, product: str) -> str:
    """Create prompt for topic extraction."""
    return (
        f"What is the main topic (e.g., Battery, Screen, Price, Service, Quality, Delivery) "
        f"of this review for the {product}? Answer efficiently in 1-3 words.\n\n"
        f"Review: {text}"
    )

def create_summary_prompt(text: str, product: str) -> str:
    """Create prompt for summarization."""
    return f"Summarize this review of the {product} in one concise sentence.\n\nReview: {text}"

# ============== API Endpoints ==============

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Check API and Ollama service health.
    
    Returns the current status of the API and whether Ollama is accessible.
    """
    ollama_online = await check_ollama_status()
    
    return {
        "status": "ok",
        "message": "Product Review Analyzer API is running",
        "version": "2.0.0",
        "ollama_status": "online" if ollama_online else "offline"
    }

@app.post("/analyze/", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_review(request: ReviewRequest):
    """
    Analyze a single product review.
    
    Performs sentiment analysis, topic extraction, and summarization on the provided review.
    
    - **text**: The review text to analyze (3-5000 characters)
    - **product_name**: Optional name of the product being reviewed
    
    Returns sentiment, main topic, and a concise summary.
    """
    text = request.text.strip()
    product = request.product_name or "Product"
    
    logger.info(f"Analyzing review for product: {product}")
    
    # Create prompts
    sentiment_prompt = create_sentiment_prompt(text, product)
    topic_prompt = create_topic_prompt(text, product)
    summary_prompt = create_summary_prompt(text, product)

    # Run queries in parallel for efficiency
    try:
        sentiment, topic, summary = await asyncio.gather(
            query_ollama(sentiment_prompt),
            query_ollama(topic_prompt),
            query_ollama(summary_prompt)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    logger.info(f"Analysis complete - Sentiment: {sentiment}, Topic: {topic}")
    
    return {
        "sentiment": sentiment,
        "topic": topic,
        "summary": summary
    }

@app.post("/analyze_batch/", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def analyze_batch(request: BatchReviewRequest):
    """
    Analyze multiple product reviews in batch.
    
    Processes each review sequentially to avoid overloading the local LLM.
    Each review's sentiment, topic, and summary queries run in parallel.
    
    - **reviews**: List of review objects (max 100 reviews)
    
    Returns analysis results for all reviews with success/error counts.
    """
    results = []
    success_count = 0
    error_count = 0
    
    logger.info(f"Starting batch analysis of {len(request.reviews)} reviews")
    
    # Processing sequentially to avoid overloading local LLM
    for idx, item in enumerate(request.reviews):
        text = item.text.strip()
        product = item.product_name or "Product"
        
        try:
            # Create prompts
            sentiment_prompt = create_sentiment_prompt(text, product)
            topic_prompt = create_topic_prompt(text, product)
            summary_prompt = create_summary_prompt(text, product)
            
            # For each review, parallelize its 3 analysis components
            sentiment, topic, summary = await asyncio.gather(
                query_ollama(sentiment_prompt),
                query_ollama(topic_prompt),
                query_ollama(summary_prompt)
            )
            
            results.append({
                "review": text,
                "product_name": product,
                "sentiment": sentiment,
                "topic": topic,
                "summary": summary,
                "error": None
            })
            success_count += 1
            
            if (idx + 1) % 10 == 0:
                logger.info(f"Processed {idx + 1}/{len(request.reviews)} reviews")
                
        except Exception as e:
            logger.error(f"Error processing review {idx + 1}: {e}")
            results.append({
                "review": text,
                "product_name": product,
                "sentiment": "Error",
                "topic": "Error",
                "summary": "Error",
                "error": str(e)
            })
            error_count += 1
    
    logger.info(f"Batch analysis complete: {success_count} successful, {error_count} errors")
    
    return {
        "results": results,
        "total_count": len(request.reviews),
        "success_count": success_count,
        "error_count": error_count
    }

@app.get("/models/", tags=["System"])
async def list_models():
    """
    List available Ollama models.
    
    Returns the list of models currently available in Ollama.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch models")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
