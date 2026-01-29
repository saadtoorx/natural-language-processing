@echo off
echo ===========================================
echo   Starting Product Review Analyzer...
echo ===========================================
echo.

echo 1. Checking for Ollama...
curl -s http://localhost:11434/api/tags > nul
if %errorlevel% neq 0 (
    echo [WARNING] Ollama does not seem to be running at localhost:11434.
    echo Please make sure Ollama is started!
    echo.
) else (
    echo [OK] Ollama found.
)

echo 2. Starting Backend (FastAPI)...
start "Backend API" cmd /k "uvicorn backend.main:app --reload"

echo 3. Starting Frontend (Streamlit)...
start "Frontend Dashboard" cmd /k "streamlit run frontend/app.py"

echo.
echo ===========================================
echo   App launched! 
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:8000
echo ===========================================
echo.
pause
