# LLaMA Text Summarizer

A production-ready text summarization application powered by a local LLaMA model via Ollama. Features a FastAPI backend and a modern Streamlit frontend.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.127+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.49+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 📝 **Text Summarization** - Summarize any text with AI
- 📄 **PDF Support** - Upload and summarize PDF documents
- 🔄 **Multiple Modes** - Brief, Detailed, or Bullet Points
- 🌐 **Multi-language** - Auto-detects language and responds accordingly
- 🌙 **Dark Mode** - Toggle dark/light theme
- 📜 **History** - View your last 5 summaries
- 💾 **Download** - Save summaries as TXT files
- 🔒 **Privacy** - All processing happens locally

## 🏗️ Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐     HTTP      ┌─────────────────┐
│                 │   POST/GET    │                 │   /api        │                 │
│   Streamlit     │ ────────────▶ │    FastAPI      │ ────────────▶ │     Ollama      │
│   Frontend      │               │    Backend      │               │     (LLaMA)     │
│   (Port 8501)   │ ◀──────────── │   (Port 8000)   │ ◀──────────── │   (Port 11434)  │
│                 │     JSON      │                 │     JSON      │                 │
└─────────────────┘               └─────────────────┘               └─────────────────┘
```

## 📋 Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Ollama** - [Install Ollama](https://ollama.ai/download)
- **LLaMA 2 Model** - Run `ollama pull llama2` after installing Ollama

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/saadtoorx/llama-text-summarizer.git
cd llama-text-summarizer
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
| POST | `/summarize/` | Summarize text |
| POST | `/summarize/pdf/` | Summarize PDF file |

## 🎨 Screenshots

*Coming soon*

## 🛠️ Configuration

Environment variables (set in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama2` | Model to use |
| `BACKEND_URL` | `http://localhost:8000` | Backend API URL |
| `MAX_TEXT_LENGTH` | `10000` | Max input characters |
| `MIN_TEXT_LENGTH` | `10` | Min input characters |

## 📁 Project Structure

```
llama-text-summarizer/
├── backend/
│   ├── __init__.py
│   └── main.py          # FastAPI application
├── frontend/
│   └── app.py           # Streamlit application
├── .env.example         # Environment template
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM runner
- [Meta AI](https://ai.meta.com/) - LLaMA model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Streamlit](https://streamlit.io/) - Data app framework
