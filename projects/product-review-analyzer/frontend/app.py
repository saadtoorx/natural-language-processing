import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="Product Review Analyzer",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for history
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Sample reviews for quick testing
SAMPLE_REVIEWS = [
    {"text": "Amazing battery life! Lasts 2 days on a single charge. Best phone I've ever owned.", "label": "Positive"},
    {"text": "The screen is too dim and the camera quality is disappointing. Not worth the price.", "label": "Negative"},
    {"text": "Good build quality but the software has some bugs. Overall decent for the price.", "label": "Mixed"}
]

def load_sample(text):
    """Callback to load sample review text."""
    st.session_state.review_input = text

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main theme */
    .main {
        /* Standard Streamlit background */
    }
    
    .stApp {
        /* Standard Streamlit background */
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .metric-card h3 {
        color: #667eea;
        font-size: 2em;
        margin-bottom: 10px;
    }
    
    .metric-card p {
        color: rgba(255,255,255,0.8);
        font-size: 1.1em;
    }
    
    /* Result cards */
    .result-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid;
        margin: 10px 0;
        backdrop-filter: blur(10px);
    }
    
    .result-positive { border-color: #00d26a; background: rgba(0, 210, 106, 0.1); }
    .result-negative { border-color: #ff6b6b; background: rgba(255, 107, 107, 0.1); }
    .result-neutral { border-color: #feca57; background: rgba(254, 202, 87, 0.1); }
    
    /* History card */
    .history-card {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Sample button */
    .sample-btn {
        background: rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 10px 15px;
        border-radius: 8px;
        color: white;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .sample-btn:hover {
        background: rgba(102, 126, 234, 0.4);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: rgba(255,255,255,0.5);
        border-top: 1px solid rgba(255,255,255,0.1);
        margin-top: 50px;
    }
    
    /* Stats box */
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px 25px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    
    .stats-number {
        font-size: 2em;
        font-weight: bold;
    }
    
    /* Progress bar customization */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Text area */
    .stTextArea textarea {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        color: white;
    }
    
    /* Input fields */
    .stTextInput input {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 10px;
        color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def get_sentiment_color(sentiment):
    """Return color based on sentiment."""
    sentiment_lower = sentiment.lower() if sentiment else ""
    if "positive" in sentiment_lower:
        return "#00d26a", "result-positive"
    elif "negative" in sentiment_lower:
        return "#ff6b6b", "result-negative"
    else:
        return "#feca57", "result-neutral"

def add_to_history(review_text, product_name, result):
    """Add analysis to session history."""
    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "product": product_name,
        "review": review_text[:50] + "..." if len(review_text) > 50 else review_text,
        "sentiment": result.get("sentiment", "N/A"),
        "topic": result.get("topic", "N/A")
    }
    st.session_state.analysis_history.insert(0, entry)
    # Keep only last 10 entries
    st.session_state.analysis_history = st.session_state.analysis_history[:10]

def create_word_cloud_chart(topics):
    """Create a simple word frequency bar chart as word cloud alternative."""
    topic_counts = pd.Series(topics).value_counts().head(10)
    fig = go.Figure(data=[
        go.Bar(
            x=topic_counts.values,
            y=topic_counts.index,
            orientation='h',
            marker=dict(
                color=topic_counts.values,
                colorscale='Viridis',
                showscale=False
            )
        )
    ])
    fig.update_layout(
        title="Topic Distribution",
        xaxis_title="Frequency",
        yaxis_title="Topics",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    return fig

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🛍️ **Analyzer Pro**")
    st.markdown("---")
    
    page = st.radio(
        "📍 Navigation",
        ["🏠 Home", "🔍 Single Review", "📂 Batch Analysis", "📜 History"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # API Status Check
    st.markdown("### ⚙️ System Status")
    try:
        health = requests.get(f"{API_URL}/", timeout=2)
        if health.status_code == 200:
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
    
    st.info("🤖 Model: **Mistral** (Ollama)")
    
    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    st.metric("Analyses", len(st.session_state.analysis_history))

# Home Page
if page == "🏠 Home":
    st.markdown("# Welcome to Product Review Analyzer 🚀")
    st.markdown("##### Analyze customer reviews with the power of AI")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    This application uses **FastAPI** and **Ollama (Mistral)** to provide deep insights into customer reviews.
    Understand sentiment, extract topics, and generate summaries instantly.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('''
        <div class="metric-card">
            <h3>💭</h3>
            <p><strong>Sentiment</strong></p>
            <p style="font-size:0.9em; opacity:0.7;">Positive, Negative, Neutral classification</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="metric-card">
            <h3>🏷️</h3>
            <p><strong>Topics</strong></p>
            <p style="font-size:0.9em; opacity:0.7;">Extract main discussion topics</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown('''
        <div class="metric-card">
            <h3>📝</h3>
            <p><strong>Summary</strong></p>
            <p style="font-size:0.9em; opacity:0.7;">Concise review summaries</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown('''
        <div class="metric-card">
            <h3>📊</h3>
            <p><strong>Insights</strong></p>
            <p style="font-size:0.9em; opacity:0.7;">Visual analytics & charts</p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Quick Start Guide
    st.markdown("### 🎯 Quick Start Guide")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("""
        **Single Review Analysis**
        1. Navigate to 🔍 Single Review
        2. Enter product name and review text
        3. Or use sample reviews for quick testing
        4. Click Analyze and view results
        """)
    
    with col_b:
        st.markdown("""
        **Batch Analysis**
        1. Navigate to 📂 Batch Analysis
        2. Upload a CSV file with reviews
        3. Map your columns
        4. Get charts and download reports
        """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Built with ❤️ using Streamlit & FastAPI | Powered by Ollama (Mistral)</p>
        <p style="font-size:0.8em;">Product Review Analyzer v2.0</p>
    </div>
    """, unsafe_allow_html=True)

# Single Review Page
elif page == "🔍 Single Review":
    st.markdown("# 🔍 Single Review Analysis")
    st.markdown("Analyze individual reviews with instant AI-powered insights.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Sample Reviews Section
    with st.expander("💡 Try Sample Reviews", expanded=False):
        st.markdown("Click any sample to auto-fill the review field:")
        
        sample_cols = st.columns(len(SAMPLE_REVIEWS))
        for idx, (col, sample) in enumerate(zip(sample_cols, SAMPLE_REVIEWS)):
            with col:
                st.button(
                    f"{sample['label']}", 
                    key=f"sample_{idx}", 
                    help=sample['text'][:50],
                    on_click=load_sample,
                    args=(sample['text'],),
                    use_container_width=True
                )
    
    st.markdown("---")
    
    # Input Section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        product_name = st.text_input(
            "🏷️ Product/Service Name",
            placeholder="e.g. iPhone 15, AirPods Pro",
            help="Enter the product or service being reviewed"
        )
    
    with col2:
        pass
    
    # Text Input with session state key
    review_text = st.text_area(
        "📝 Enter Review Text:",
        key="review_input",
        height=150,
        placeholder="Paste or type the review here...\n\nExample: The battery life is amazing, but the screen is a bit dim for outdoor use."
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        analyze_clicked = st.button("🚀 Analyze Review", type="primary")
    
    with col_btn2:
        if st.button("🗑️ Clear"):
            st.rerun()
    
    if analyze_clicked:
        if review_text.strip():
            with st.spinner("🔄 Analyzing review..."):
                try:
                    payload = {"text": review_text}
                    if product_name:
                        payload["product_name"] = product_name
                    
                    response = requests.post(f"{API_URL}/analyze/", json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Add to history
                        add_to_history(review_text, product_name or "Product", data)
                        
                        st.markdown("---")
                        st.markdown("### 📊 Analysis Results")
                        
                        # Get sentiment styling
                        sentiment_color, sentiment_class = get_sentiment_color(data.get('sentiment', ''))
                        
                        c1, c2, c3 = st.columns(3)
                        
                        with c1:
                            st.markdown(f'''
                            <div class="result-card {sentiment_class}">
                                <h4 style="margin:0; color:{sentiment_color};">💭 Sentiment</h4>
                                <p style="font-size:1.5em; font-weight:bold; margin:10px 0;">{data.get('sentiment', 'N/A')}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        with c2:
                            st.markdown(f'''
                            <div class="result-card result-neutral">
                                <h4 style="margin:0; color:#feca57;">🏷️ Topic</h4>
                                <p style="font-size:1.5em; font-weight:bold; margin:10px 0;">{data.get('topic', 'N/A')}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        with c3:
                            st.markdown(f'''
                            <div class="result-card" style="border-color: #667eea;">
                                <h4 style="margin:0; color:#667eea;">📝 Summary</h4>
                                <p style="margin:10px 0;">{data.get('summary', 'N/A')}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                        
                        st.success("✅ Analysis complete! Check the History tab to view past analyses.")
                    else:
                        st.error(f"❌ Error {response.status_code}: {response.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("❌ Connection Error: Make sure the backend server is running on localhost:8000")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Please enter a review to analyze.")

# Batch Analysis Page
elif page == "📂 Batch Analysis":
    st.markdown("# 📂 Batch Analysis")
    st.markdown("Upload a CSV file to analyze multiple reviews at once with visual insights.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # File Upload
    uploaded_file = st.file_uploader(
        "📁 Upload CSV File",
        type=["csv"],
        help="Upload a CSV file containing product reviews"
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        
        st.markdown("### 👀 Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        
        st.markdown(f"**Total Reviews:** {len(df)}")
        
        st.markdown("---")
        
        # Column Mapping
        st.markdown("### 🔗 Column Mapping")
        all_columns = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            review_col = st.selectbox(
                "📝 Review Text Column",
                all_columns,
                index=all_columns.index("review_text") if "review_text" in all_columns else 0,
                help="Select the column containing review text"
            )
        
        with col2:
            product_col = st.selectbox(
                "🏷️ Product Name Column (Optional)",
                ["None"] + all_columns,
                index=(all_columns.index("product_name") + 1) if "product_name" in all_columns else 0,
                help="Select the column containing product names"
            )
        
        st.markdown("---")
        
        if st.button("🚀 Start Batch Analysis", type="primary"):
            reviews = df[review_col].fillna("").astype(str).tolist()
            
            # Prepare payload
            batch_payload = []
            if product_col != "None":
                products = df[product_col].fillna("Product").astype(str).tolist()
                for r, p in zip(reviews, products):
                    batch_payload.append({"text": r, "product_name": p})
            else:
                for r in reviews:
                    batch_payload.append({"text": r, "product_name": "Product"})
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text(f"🔄 Processing {len(reviews)} reviews... This may take a moment.")
            
            try:
                response = requests.post(
                    f"{API_URL}/analyze_batch/",
                    json={"reviews": batch_payload},
                    timeout=3000
                )
                
                progress_bar.progress(100)
                
                if response.status_code == 200:
                    results_data = response.json()["results"]
                    
                    # Merge results
                    final_df = df.copy()
                    final_df["Sentiment"] = [r.get("sentiment", "Error") for r in results_data]
                    final_df["Summary"] = [r.get("summary", "Error") for r in results_data]
                    
                    # Add to history
                    batch_name = uploaded_file.name if uploaded_file else "Batch File"
                    add_to_history(
                        f"Analysis of {len(reviews)} reviews from {batch_name}", 
                        "Batch Analysis", 
                        {"sentiment": "Mixed", "topic": f"{len(reviews)} Items"}
                    )
                    
                    status_text.empty()
                    st.success("✅ Analysis Complete!")
                    
                    # Dashboard Section
                    st.markdown("---")
                    st.markdown("### 📊 Analytics Dashboard")
                    
                    # Stats Row
                    stat_cols = st.columns(4)
                    
                    sentiment_counts = final_df["Sentiment"].value_counts()
                    
                    with stat_cols[0]:
                        st.markdown(f'''
                        <div class="stats-box">
                            <div class="stats-number">{len(final_df)}</div>
                            <div>Total Reviews</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with stat_cols[1]:
                        positive_count = sum(1 for s in final_df["Sentiment"] if "positive" in s.lower())
                        st.markdown(f'''
                        <div class="stats-box" style="background: linear-gradient(135deg, #00d26a 0%, #00a854 100%);">
                            <div class="stats-number">{positive_count}</div>
                            <div>Positive</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with stat_cols[2]:
                        negative_count = sum(1 for s in final_df["Sentiment"] if "negative" in s.lower())
                        st.markdown(f'''
                        <div class="stats-box" style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);">
                            <div class="stats-number">{negative_count}</div>
                            <div>Negative</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with stat_cols[3]:
                        neutral_count = len(final_df) - positive_count - negative_count
                        st.markdown(f'''
                        <div class="stats-box" style="background: linear-gradient(135deg, #feca57 0%, #f39c12 100%);">
                            <div class="stats-number">{neutral_count}</div>
                            <div>Neutral/Mixed</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Charts
                    chart_col1, chart_col2 = st.columns(2)
                    
                    with chart_col1:
                        # Sentiment Pie Chart
                        sentiment_summary = final_df["Sentiment"].apply(
                            lambda x: "Positive" if "positive" in x.lower() 
                            else ("Negative" if "negative" in x.lower() else "Neutral")
                        ).value_counts().reset_index()
                        sentiment_summary.columns = ["Sentiment", "Count"]
                        
                        colors = {"Positive": "#00d26a", "Negative": "#ff6b6b", "Neutral": "#feca57"}
                        
                        fig_pie = px.pie(
                            sentiment_summary,
                            values="Count",
                            names="Sentiment",
                            title="Sentiment Distribution",
                            hole=0.4,
                            color="Sentiment",
                            color_discrete_map=colors
                        )
                        fig_pie.update_layout(
                            template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with chart_col2:
                        # Topic Bar Chart
                        fig_topics = create_word_cloud_chart(final_df["Topic"].tolist())
                        st.plotly_chart(fig_topics, use_container_width=True)
                    
                    # Data Table with Filtering
                    st.markdown("---")
                    st.markdown("### 📋 Detailed Results")
                    
                    # Filter options
                    filter_col1, filter_col2 = st.columns(2)
                    
                    with filter_col1:
                        sentiment_filter = st.multiselect(
                            "Filter by Sentiment",
                            options=["All", "Positive", "Negative", "Neutral"],
                            default=["All"]
                        )
                    
                    with filter_col2:
                        search_term = st.text_input("🔍 Search in reviews", placeholder="Enter keyword...")
                    
                    # Apply filters
                    filtered_df = final_df.copy()
                    
                    if "All" not in sentiment_filter and sentiment_filter:
                        filtered_df = filtered_df[
                            filtered_df["Sentiment"].apply(
                                lambda x: any(s.lower() in x.lower() for s in sentiment_filter)
                            )
                        ]
                    
                    if search_term:
                        filtered_df = filtered_df[
                            filtered_df[review_col].str.contains(search_term, case=False, na=False)
                        ]
                    
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                    
                    # Download Section
                    st.markdown("---")
                    st.markdown("### 📥 Export Results")
                    
                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        csv = final_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download Full Report (CSV)",
                            csv,
                            f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            "text/csv",
                            key='download-csv'
                        )
                    
                    with col_dl2:
                        # Summary stats
                        summary_text = f"""Product Review Analysis Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Reviews Analyzed: {len(final_df)}
Positive Reviews: {positive_count} ({positive_count/len(final_df)*100:.1f}%)
Negative Reviews: {negative_count} ({negative_count/len(final_df)*100:.1f}%)
Neutral Reviews: {neutral_count} ({neutral_count/len(final_df)*100:.1f}%)

Top Topics:
{chr(10).join([f'- {topic}' for topic in final_df['Topic'].value_counts().head(5).index.tolist()])}
"""
                        st.download_button(
                            "📊 Download Summary (TXT)",
                            summary_text,
                            f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            "text/plain",
                            key='download-txt'
                        )
                
                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Try with fewer reviews.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Make sure the backend server is running.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# History Page
elif page == "📜 History":
    st.markdown("# 📜 Analysis History")
    st.markdown("View your recent analysis results from this session.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.analysis_history:
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
        
        st.markdown("---")
        
        for idx, entry in enumerate(st.session_state.analysis_history):
            sentiment_color, _ = get_sentiment_color(entry['sentiment'])
            
            st.markdown(f'''
            <div class="history-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="color: rgba(255,255,255,0.5); font-size: 0.9em;">🕐 {entry['timestamp']}</span>
                        <span style="margin-left: 15px; color: rgba(255,255,255,0.7);">📦 {entry['product']}</span>
                    </div>
                    <span style="color: {sentiment_color}; font-weight: bold;">{entry['sentiment']}</span>
                </div>
                <p style="margin: 10px 0 5px 0; color: rgba(255,255,255,0.9);">"{entry['review']}"</p>
                <p style="margin: 0; color: rgba(255,255,255,0.6); font-size: 0.9em;">Topic: {entry['topic']}</p>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("📭 No analysis history yet. Analyze some reviews to see them here!")
        
        st.markdown("""
        ### 💡 How to get started:
        1. Go to **🔍 Single Review** page
        2. Enter a product review
        3. Click **Analyze Review**
        4. Your results will appear here!
        """)

# Footer (shown on all pages except home which has its own)
if page != "🏠 Home":
    st.markdown("""
    <div class="footer">
        <p>Product Review Analyzer v2.0 | Built by Saad Toor (saadtoorx)</p>
    </div>
    """, unsafe_allow_html=True)
