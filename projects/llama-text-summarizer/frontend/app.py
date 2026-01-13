import streamlit as st
import requests
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="LLaMA Text Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def apply_custom_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main-header {
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
        }
        
        /* Stats cards */
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .stat-card h3 {
            margin: 0;
            font-size: 1.5rem;
        }
        
        .stat-card p {
            margin: 0;
            opacity: 0.9;
            font-size: 0.9rem;
        }
        
        /* Summary box */
        .summary-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1.5rem;
            border-radius: 0 10px 10px 0;
            margin: 1rem 0;
        }
        
        /* History item */
        .history-item {
            background: #f1f3f4;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            font-size: 0.85rem;
        }
        
        /* Character counter */
        .char-counter {
            font-size: 0.85rem;
            color: #666;
            text-align: right;
            margin-top: -0.5rem;
        }
        
        .char-counter.warning {
            color: #ff6b6b;
        }
        
        /* Mode selector styling */
        .stRadio > div {
            display: flex;
            gap: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_css()

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


def check_backend_health():
    """Check if the backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json() if response.ok else None
    except:
        return None


def summarize_text(text: str, mode: str) -> dict:
    """Call the backend API to summarize text."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/summarize/",
            data={"text": text, "mode": mode},
            timeout=120
        )
        if response.ok:
            return {"success": True, "data": response.json()}
        else:
            error_detail = response.json().get("detail", "Unknown error occurred")
            return {"success": False, "error": error_detail}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to backend. Please ensure the server is running."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. The text might be too long."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def summarize_pdf(file, mode: str) -> dict:
    """Call the backend API to summarize PDF."""
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = requests.post(
            f"{BACKEND_URL}/summarize/pdf/",
            files=files,
            data={"mode": mode},
            timeout=120
        )
        if response.ok:
            return {"success": True, "data": response.json()}
        else:
            error_detail = response.json().get("detail", "Unknown error occurred")
            return {"success": False, "error": error_detail}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to backend. Please ensure the server is running."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. The PDF might be too large."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def add_to_history(text_preview: str, summary: str, mode: str, language: str):
    """Add a summary to history."""
    st.session_state.history.insert(0, {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "preview": text_preview[:50] + "..." if len(text_preview) > 50 else text_preview,
        "summary": summary,
        "mode": mode,
        "language": language
    })
    # Keep only last 5 entries
    st.session_state.history = st.session_state.history[:5]


# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    # Dark mode toggle
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.divider()
    
    # Backend status
    st.markdown("### 🔌 Backend Status")
    health = check_backend_health()
    if health:
        st.success(f"✅ API: {health['status']}")
        ollama_status = health.get('ollama_status', 'unknown')
        if ollama_status == 'healthy':
            st.success(f"✅ Ollama: {ollama_status}")
        else:
            st.warning(f"⚠️ Ollama: {ollama_status}")
    else:
        st.error("❌ Backend is not running")
        st.info("Start the backend with:\n`uvicorn backend.main:app --reload`")
    
    st.divider()
    
    # History
    st.markdown("### 📜 Recent Summaries")
    if st.session_state.history:
        for i, item in enumerate(st.session_state.history):
            with st.expander(f"🕐 {item['timestamp']} - {item['mode'].title()}", expanded=False):
                st.markdown(f"**Input:** {item['preview']}")
                st.markdown(f"**Language:** {item['language']}")
                st.markdown(f"**Summary:** {item['summary'][:100]}...")
                if st.button("📋 Copy", key=f"copy_history_{i}"):
                    st.code(item['summary'])
    else:
        st.caption("No summaries yet. Start summarizing!")
    
    if st.session_state.history:
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()


# Main content
st.markdown("""
<div class="main-header">
    <h1>📝 LLaMA Text Summarizer</h1>
    <p style="color: #666; font-size: 1.1rem;">Powered by local LLaMA model via Ollama</p>
</div>
""", unsafe_allow_html=True)

# Input mode tabs
tab1, tab2 = st.tabs(["📝 Text Input", "📄 PDF Upload"])

with tab1:
    # Summary mode selector
    col1, col2 = st.columns([3, 1])
    with col1:
        summary_mode = st.radio(
            "Summary Mode",
            options=["brief", "detailed", "bullets"],
            format_func=lambda x: {"brief": "📌 Brief (2-3 sentences)", "detailed": "📖 Detailed", "bullets": "📋 Bullet Points"}[x],
            horizontal=True,
            key="text_mode"
        )
    
    # Text input
    user_input = st.text_area(
        "Enter your text here:",
        height=200,
        placeholder="Paste your article, document, or any text you want to summarize...",
        key="text_input"
    )
    
    # Character counter
    char_count = len(user_input)
    max_chars = 10000
    counter_class = "warning" if char_count > max_chars else ""
    st.markdown(f'<p class="char-counter {counter_class}">{char_count:,} / {max_chars:,} characters</p>', unsafe_allow_html=True)
    
    # Progress bar
    progress = min(char_count / max_chars, 1.0)
    st.progress(progress)
    
    # Summarize button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        summarize_btn = st.button(
            "✨ Summarize Text",
            type="primary",
            use_container_width=True,
            disabled=len(user_input.strip()) < 10
        )
    
    if summarize_btn:
        if not user_input.strip():
            st.error("⚠️ Please enter some text to summarize.")
        else:
            with st.spinner("🔄 Generating summary... This may take a moment."):
                result = summarize_text(user_input, summary_mode)
            
            if result["success"]:
                data = result["data"]
                
                # Stats row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{data['original_length']:,}</h3>
                        <p>Original Chars</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{data['summary_length']:,}</h3>
                        <p>Summary Chars</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    reduction = round((1 - data['summary_length'] / data['original_length']) * 100, 1)
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{reduction}%</h3>
                        <p>Reduction</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{data['language'].upper()}</h3>
                        <p>Language</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Summary display
                st.subheader("📝 Summary")
                st.markdown(f'<div class="summary-box">{data["summary"]}</div>', unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="💾 Download as TXT",
                        data=data["summary"],
                        file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                with col2:
                    if st.button("📋 Copy to Clipboard"):
                        st.code(data["summary"])
                        st.success("Text displayed above - select and copy!")
                
                # Add to history
                add_to_history(user_input, data["summary"], data["mode"], data["language"])
            else:
                st.error(f"❌ {result['error']}")

with tab2:
    # Summary mode selector for PDF
    summary_mode_pdf = st.radio(
        "Summary Mode",
        options=["brief", "detailed", "bullets"],
        format_func=lambda x: {"brief": "📌 Brief (2-3 sentences)", "detailed": "📖 Detailed", "bullets": "📋 Bullet Points"}[x],
        horizontal=True,
        key="pdf_mode"
    )
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        help="Upload a PDF document to extract and summarize its text content."
    )
    
    if uploaded_file:
        st.info(f"📄 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            summarize_pdf_btn = st.button(
                "✨ Summarize PDF",
                type="primary",
                use_container_width=True
            )
        
        if summarize_pdf_btn:
            with st.spinner("🔄 Extracting text and generating summary..."):
                result = summarize_pdf(uploaded_file, summary_mode_pdf)
            
            if result["success"]:
                data = result["data"]
                
                # Stats row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{data['original_length']:,}</h3>
                        <p>Extracted Chars</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{data['summary_length']:,}</h3>
                        <p>Summary Chars</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    reduction = round((1 - data['summary_length'] / data['original_length']) * 100, 1)
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{reduction}%</h3>
                        <p>Reduction</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    st.markdown(f"""
                    <div class="stat-card">
                        <h3>{data['language'].upper()}</h3>
                        <p>Language</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Summary display
                st.subheader("📝 Summary")
                st.markdown(f'<div class="summary-box">{data["summary"]}</div>', unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.download_button(
                        label="💾 Download as TXT",
                        data=data["summary"],
                        file_name=f"summary_{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                with col2:
                    if st.button("📋 Copy to Clipboard", key="copy_pdf"):
                        st.code(data["summary"])
                        st.success("Text displayed above - select and copy!")
                
                # Add to history
                add_to_history(f"[PDF] {uploaded_file.name}", data["summary"], data["mode"], data["language"])
            else:
                st.error(f"❌ {result['error']}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    <p>Built with ❤️ using FastAPI, Streamlit & Ollama</p>
    <p>🔒 Your data stays local - no cloud processing</p>
</div>
""", unsafe_allow_html=True)