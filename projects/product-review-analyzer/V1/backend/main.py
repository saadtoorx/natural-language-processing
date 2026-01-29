from fastapi import FastAPI, Form
import requests

app = FastAPI()

def query_ollama(prompt: str):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"].strip()

@app.post("/analyze/")
def analyze_review(text: str = Form(...)):
    sentiment_prompt = (
        "What is the sentiment (Positive, Neutral, or Negative) of the following review?\n\n"
        f"{text}"
    )

    topic_prompt = (
        "What is the main issue or topic discussed in this review?\n\n"
        f"{text}"
    )

    summary_prompt = (
        "Summarize the following review in one short sentence:\n\n"
        f"{text}"
    )

    sentiment = query_ollama(sentiment_prompt)
    topic = query_ollama(topic_prompt)
    summary = query_ollama(summary_prompt)

    return {
        "sentiment": sentiment,
        "topic": topic,
        "summary": summary
    }