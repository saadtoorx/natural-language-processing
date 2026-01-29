# 🛒 Product Review Analyzer

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B)
![Ollama](https://img.shields.io/badge/AI-Ollama-black)
![License](https://img.shields.io/badge/License-MIT-green)

A specific, powerful, and AI-driven application designed to analyze product reviews using **FastAPI**, **Streamlit**, and **Ollama (Mistral)**. Gain instant insights into customer sentiment, extract key topics, and generate concise summaries.

---

## 🚀 Features

- **🎨 Modern Dashboards**: Beautiful, gradient-themed UI with dark mode support.
- **⚡ Async Processing**: Fast, non-blocking analysis using Python's asyncio.
- **🔍 Single Review Analysis**: Instant feedback on sentiment, topic, and summary.
- **📂 Batch & Bulk Analysis**: Upload CSV files to analyze hundreds of reviews simultaneously.
- **📊 Interactive Visualizations**:
  - Sentiment Distribution Pie Charts
  - Topic Word/Bar Charts
  - Filtering and Search Capabilities
- **🧙‍♂️ Smart Features**:
  - **Quick-Fill Samples**: Test instantly with built-in example reviews.
  - **Session History**: Keep track of your recent analyses.
  - **Export Reports**: Download full analysis results as CSV or summary text files.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (UI), Plotly (Charts)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (API), Uvicorn (Server)
- **AI Engine**: [Ollama](https://ollama.ai/) running **Mistral**
- **Data Handling**: Pandas

---

## 📋 Prerequisites

1. **Python 3.9+** installed.
2. **Ollama** installed and running locally.
   - [Download Ollama](https://ollama.com)
   - Pull the model:
     ```bash
     ollama pull mistral
     ```

---

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/product-review-analyzer.git
   cd product-review-analyzer
   ```

2. **Set up a virtual environment** (Optional but recommended):

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

### Quick Start (Windows)

Simply run the included batch script:

```bash
start_app.bat
```

This launches both the Backend (Port 8000) and Frontend (Port 8501).

### Manual Start

**1. Start the Backend API:**

```bash
uvicorn backend.main:app --reload
```

_API Docs available at: http://localhost:8000/docs_

**2. Start the Frontend UI:**

```bash
streamlit run frontend/app.py
```

_Access the app at: http://localhost:8501_

---

## 📂 Project Structure

```
product-review-analyzer/
├── backend/
│   └── main.py          # FastAPI Application & Logic
├── frontend/
│   └── app.py           # Streamlit Dashboard UI
├── V1/                  # Previous version of the project  
├── data/
│   └── sample_reviews.csv  # Sample data for testing
├── requirements.txt     # Python Dependencies
├── start_app.bat        # One-click launch script
├── .gitignore          # Git exclusion rules
├── LICENSE             # MIT License
└── README.md           # Documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by saadtoorx
</p>
