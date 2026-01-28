# Sentiment Analyzer AI

A production-ready sentiment analysis application powered by a local Mistral model via Ollama. Features a FastAPI backend and a modern Streamlit frontend.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.127+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 🎭 **Sentiment Analysis** - Analyze sentiment of any text with AI
- 📊 **Batch Processing** - Analyze multiple texts or upload CSV files
- 📋 **History** - Track and view your past analyses
- 📥 **Export Results** - Download results as CSV or JSON
- ⚙️ **Configurable** - Adjust model parameters (temperature, model name)
- 🔍 **Health Status** - Real-time API and model status monitoring
- 🟢 **Visual Feedback** - Color-coded sentiment indicators
- 🔒 **Privacy** - All processing happens locally

## 🏗️ Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐     HTTP      ┌─────────────────┐
│                 │   POST/GET    │                 │   /api        │                 │
│   Streamlit     │ ────────────▶ │    FastAPI      │ ────────────▶ │     Ollama      │
│   Frontend      │               │    Backend      │               │    (Mistral)    │
│   (Port 8501)   │ ◀──────────── │   (Port 8000)   │ ◀──────────── │   (Port 11434)  │
│                 │     JSON      │                 │     JSON      │                 │
└─────────────────┘               └─────────────────┘               └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Ollama** - [Install Ollama](https://ollama.ai/download)
- **Mistral Model** - Run `ollama pull mistral` after installing Ollama

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Project 2 Sentiment Analyzer AI Project"
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Start Ollama

Make sure Ollama is running:
```bash
ollama serve
```

### 6. Run the Application

**Terminal 1 - Start Backend:**
```bash
uvicorn backend.main:app --reload
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run frontend/app.py
```

### 7. Open the App

Navigate to `http://localhost:8501` in your browser.

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API and Ollama status |
| POST | `/analyze/` | Analyze single text (Form) |
| POST | `/analyze/json` | Analyze single text (JSON) |
| POST | `/analyze/batch` | Analyze multiple texts |

## 🎨 Screenshots

*Coming soon*

## 🛠️ Configuration

Environment variables (set in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API URL |
| `DEFAULT_MODEL` | `mistral` | Model to use by default |

## 📁 Project Structure

```
Sentiment Analyzer AI/
├── backend/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── frontend/
│   └── app.py           # Streamlit application
├── .env.example         # Environment template
├── .gitignore
├── README.md
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM runner
- [Mistral AI](https://mistral.ai/) - Mistral model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - Data app framework
