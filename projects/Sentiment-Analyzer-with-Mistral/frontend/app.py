"""
Sentiment Analyzer Frontend
A Streamlit app for sentiment analysis with history, batch processing, and export features.
"""

import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Sentiment Analyzer",
    page_icon="🎭",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .sentiment-positive {
        background-color: #d4edda;
        color: #155724;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
    }
    .sentiment-negative {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
    }
    .sentiment-neutral {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: bold;
        text-align: center;
    }
    .sentiment-error {
        background-color: #f5f5f5;
        color: #6c757d;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 1.2em;
        text-align: center;
    }
    .status-online {
        color: #28a745;
        font-weight: bold;
    }
    .status-offline {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": "mistral",
        "temperature": 0.7
    }


def check_api_health():
    """Check if API and Ollama are running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return {"api_status": "offline", "ollama_status": "offline", "model": "unknown"}


def analyze_single(text: str) -> dict:
    """Analyze a single text."""
    try:
        response = requests.post(
            f"{API_URL}/analyze/json",
            json={
                "text": text,
                "model": st.session_state.settings["model"],
                "temperature": st.session_state.settings["temperature"]
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        return {"text": text, "sentiment": "Error: API not running", "success": False}
    except Exception as e:
        return {"text": text, "sentiment": f"Error: {str(e)}", "success": False}
    return {"text": text, "sentiment": "Error: Unknown", "success": False}


def analyze_batch(texts: list) -> list:
    """Analyze multiple texts."""
    try:
        response = requests.post(
            f"{API_URL}/analyze/batch",
            json={
                "texts": texts,
                "model": st.session_state.settings["model"],
                "temperature": st.session_state.settings["temperature"]
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json()["results"]
    except:
        pass
    return [{"text": t, "sentiment": "Error", "success": False} for t in texts]


def get_sentiment_display(sentiment: str) -> str:
    """Return styled HTML for sentiment display."""
    sentiment_lower = sentiment.lower()
    if "positive" in sentiment_lower:
        return f'<div class="sentiment-positive">🟢 {sentiment}</div>'
    elif "negative" in sentiment_lower:
        return f'<div class="sentiment-negative">🔴 {sentiment}</div>'
    elif "neutral" in sentiment_lower:
        return f'<div class="sentiment-neutral">🟡 {sentiment}</div>'
    else:
        return f'<div class="sentiment-error">⚪ {sentiment}</div>'


def add_to_history(text: str, sentiment: str):
    """Add analysis result to history."""
    st.session_state.history.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text[:100] + "..." if len(text) > 100 else text,
        "full_text": text,
        "sentiment": sentiment
    })
    # Keep only last 50 entries
    st.session_state.history = st.session_state.history[:50]


# Sidebar - Settings & Health Check
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Health Check
    st.subheader("🔍 API Status")
    health = check_api_health()
    
    api_status = "🟢 Online" if health["api_status"] == "online" else "🔴 Offline"
    ollama_status = "🟢 Online" if health["ollama_status"] == "online" else "🔴 Offline"
    
    st.write(f"**API:** {api_status}")
    st.write(f"**Ollama:** {ollama_status}")
    
    st.divider()
    
    # Model Settings
    st.subheader("🤖 Model Settings")
    
    st.session_state.settings["model"] = st.text_input(
        "Model Name",
        value=st.session_state.settings["model"],
        help="The Ollama model to use (e.g., mistral, llama2)"
    )
    
    st.session_state.settings["temperature"] = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state.settings["temperature"],
        step=0.1,
        help="Higher = more creative, Lower = more consistent"
    )
    
    st.divider()
    
    # Clear History
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.success("History cleared!")


# Main Content
st.title("🎭 Sentiment Analyzer")
st.caption("Analyze text sentiment using AI powered by Ollama")

# Tabs for different features
tab1, tab2, tab3 = st.tabs(["📝 Single Analysis", "📋 Batch Analysis", "📊 History"])

# Tab 1: Single Analysis
with tab1:
    st.subheader("Analyze Single Text")
    
    # Example texts
    st.write("**Try an example:**")
    col1, col2, col3 = st.columns(3)
    
    example_texts = {
        "Positive": "I absolutely love this product! It exceeded all my expectations.",
        "Negative": "This was a terrible experience. I'm very disappointed.",
        "Neutral": "The package arrived on Tuesday. It was a regular delivery."
    }
    
    with col1:
        if st.button("😊 Positive Example", use_container_width=True):
            st.session_state.example_text = example_texts["Positive"]
    with col2:
        if st.button("😢 Negative Example", use_container_width=True):
            st.session_state.example_text = example_texts["Negative"]
    with col3:
        if st.button("😐 Neutral Example", use_container_width=True):
            st.session_state.example_text = example_texts["Neutral"]
    
    # Text input
    default_text = st.session_state.get("example_text", "")
    text_input = st.text_area(
        "Enter your text:",
        value=default_text,
        height=150,
        placeholder="Type or paste your text here..."
    )
    
    # Clear example after use
    if "example_text" in st.session_state:
        del st.session_state.example_text
    
    # Analyze button
    if st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True):
        if text_input.strip():
            with st.spinner("Analyzing sentiment..."):
                result = analyze_single(text_input)
                sentiment = result.get("sentiment", "Error")
                
                st.subheader("Result:")
                st.markdown(get_sentiment_display(sentiment), unsafe_allow_html=True)
                
                # Add to history
                if result.get("success", False):
                    add_to_history(text_input, sentiment)
        else:
            st.warning("Please enter some text to analyze.")


# Tab 2: Batch Analysis
with tab2:
    st.subheader("Analyze Multiple Texts")
    
    # Option 1: Manual input
    st.write("**Option 1: Enter multiple texts (one per line)**")
    batch_input = st.text_area(
        "Enter texts (one per line):",
        height=150,
        placeholder="First text to analyze\nSecond text to analyze\nThird text to analyze",
        key="batch_manual"
    )
    
    # Option 2: CSV upload
    st.write("**Option 2: Upload a CSV file**")
    uploaded_file = st.file_uploader(
        "Upload CSV with a 'text' column",
        type=["csv"],
        help="CSV must have a column named 'text'"
    )
    
    # Process button
    if st.button("📊 Analyze All", type="primary", use_container_width=True):
        texts_to_analyze = []
        
        # Get texts from manual input
        if batch_input.strip():
            texts_to_analyze = [t.strip() for t in batch_input.split("\n") if t.strip()]
        
        # Get texts from CSV
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                if "text" in df.columns:
                    texts_to_analyze.extend(df["text"].dropna().tolist())
                else:
                    st.error("CSV must have a 'text' column!")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        if texts_to_analyze:
            with st.spinner(f"Analyzing {len(texts_to_analyze)} texts..."):
                results = analyze_batch(texts_to_analyze)
                
                # Create results dataframe
                results_df = pd.DataFrame(results)
                
                # Add to history
                for r in results:
                    if r.get("success", False):
                        add_to_history(r["text"], r["sentiment"])
                
                # Display results
                st.subheader(f"Results ({len(results)} texts)")
                
                # Summary
                col1, col2, col3, col4 = st.columns(4)
                sentiments = [r["sentiment"].lower() for r in results]
                
                with col1:
                    st.metric("Total", len(results))
                with col2:
                    st.metric("🟢 Positive", sum(1 for s in sentiments if "positive" in s))
                with col3:
                    st.metric("🔴 Negative", sum(1 for s in sentiments if "negative" in s))
                with col4:
                    st.metric("🟡 Neutral", sum(1 for s in sentiments if "neutral" in s))
                
                # Results table
                st.dataframe(results_df[["text", "sentiment"]], use_container_width=True)
                
                # Export options
                st.subheader("📥 Export Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        "📄 Download CSV",
                        data=csv_data,
                        file_name="sentiment_results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    json_data = results_df.to_json(orient="records", indent=2)
                    st.download_button(
                        "📋 Download JSON",
                        data=json_data,
                        file_name="sentiment_results.json",
                        mime="application/json",
                        use_container_width=True
                    )
        else:
            st.warning("Please enter some texts or upload a CSV file.")


# Tab 3: History
with tab3:
    st.subheader("Analysis History")
    
    if st.session_state.history:
        # Summary chart
        sentiments = [h["sentiment"].lower() for h in st.session_state.history]
        positive = sum(1 for s in sentiments if "positive" in s)
        negative = sum(1 for s in sentiments if "negative" in s)
        neutral = sum(1 for s in sentiments if "neutral" in s)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Analyses", len(st.session_state.history))
        with col2:
            st.metric("🟢 Positive", positive)
        with col3:
            st.metric("🔴 Negative", negative)
        with col4:
            st.metric("🟡 Neutral", neutral)
        
        st.divider()
        
        # History table
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(
            history_df[["timestamp", "text", "sentiment"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Export history
        st.subheader("📥 Export History")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = history_df.to_csv(index=False)
            st.download_button(
                "📄 Download CSV",
                data=csv_data,
                file_name="sentiment_history.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = history_df.to_json(orient="records", indent=2)
            st.download_button(
                "📋 Download JSON",
                data=json_data,
                file_name="sentiment_history.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("No analysis history yet. Start analyzing some texts!")