# Contributing to Product Review Analyzer

Thank you for your interest in contributing to the Product Review Analyzer! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/product-review-analyzer.git
   cd product-review-analyzer
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📋 How to Contribute

### Reporting Bugs

- Use the GitHub Issues page
- Check if the issue already exists
- Include:
  - Clear description of the bug
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable
  - Your environment (OS, Python version, etc.)

### Suggesting Features

- Open a GitHub Issue with the "enhancement" label
- Describe the feature and its use case
- Explain why it would benefit users

### Pull Requests

1. Create a new branch for your feature:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Test your changes:
   - Ensure the backend starts: `uvicorn backend.main:app --reload`
   - Ensure the frontend works: `streamlit run frontend/app.py`
   - Test both single and batch analysis features

4. Commit your changes:

   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

5. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request on GitHub

## 💻 Coding Standards

- **Python**: Follow PEP 8 style guidelines
- **Comments**: Add docstrings to functions and classes
- **Naming**: Use descriptive variable and function names
- **Testing**: Test your changes before submitting

## 📁 Project Structure

```
product-review-analyzer/
├── backend/
│   └── main.py          # FastAPI application
├── frontend/
│   └── app.py           # Streamlit dashboard
├── data/
│   └── sample_reviews.csv
├── requirements.txt
├── start_app.bat
└── README.md
```

## 🔧 Development Tips

- **Backend API Docs**: Visit `http://localhost:8000/docs` for Swagger UI
- **Hot Reload**: Both servers support hot reload during development
- **Ollama**: Make sure Ollama is running with `mistral` model pulled

## 📝 Commit Message Format

Use clear, descriptive commit messages:

- `Add: new feature description`
- `Fix: bug description`
- `Update: what was updated`
- `Remove: what was removed`
- `Docs: documentation changes`

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

## 📧 Questions?

If you have questions, feel free to:

- Open a GitHub Issue
- Reach out to the maintainers

Thank you for contributing! 🎉
