import streamlit as st
from streamlit_option_menu import option_menu
import time
from datetime import datetime
from config.settings import settings
from workflows.graph import run_workflow
from database.models import ContentModel
from utilis.logger import WorkflowLogger
import pandas as pd
from typing import Dict, List, Optional
import logging

# ============================================================================
# CONSTANTS
# ============================================================================
CONTENT_TYPES = {
    "blog": "Blog Post",
    "article": "Article",
    "social": "Social Media"
}

CONTENT_GUIDELINES = {
    "blog": "💡 **Blog Post**: 600-1000 words, engaging and accessible tone",
    "article": "📰 **Article**: 800-1500 words, formal and professional tone",
    "social": "📱 **Social Media**: 50-280 characters, concise and catchy"
}

WORKFLOW_STAGES = {
    "research": ("🔍 Researching...", 0.16),
    "analysis": ("📊 Analyzing...", 0.32),
    "writing": ("✍️ Writing...", 0.48),
    "fact_checking": ("✅ Fact-Checking...", 0.64),
    "revision": ("🔄 Revising...", 0.80),
    "finalization": ("🎯 Finalizing...", 1.0)
}

PAGINATION_SIZE = 10
APP_VERSION = "v1.1.0"
APP_NAME = "Content Research & Writing Assistant"

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1e7dd;
        border: 1px solid #badbcc;
        color: #0f5132;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #cfe2ff;
        border: 1px solid #b6d4fe;
        color: #084298;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .metric-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def initialize_session_state():
    """Initialize all session state variables."""
    default_state = {
        'generated_content': None,
        'current_content_id': None,
        'search_query': '',
        'filter_type': 'All',
        'page_number': 1,
        'show_success': False
    }
    
    for key, value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_logger():
    """Get or create logger instance."""
    return WorkflowLogger()

def format_content_type(content_type: str) -> str:
    """Format content type for display."""
    return CONTENT_TYPES.get(content_type, content_type)

def get_guideline(content_type: str) -> str:
    """Get guideline for content type."""
    return CONTENT_GUIDELINES.get(content_type, "")

def safe_get_db():
    """Safely initialize database connection."""
    try:
        return ContentModel()
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

def validate_api_keys():
    """Validate API keys and configuration."""
    try:
        settings.validate()
        return True, "API Keys Configured"
    except ValueError as e:
        return False, f"Configuration Error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def run_content_generation(
    topic: str,
    content_type: str,
    target_audience: str,
    progress_bar,
    status_text
) -> tuple:
    """Generate content with progress tracking and error handling."""
    logger = get_logger()
    
    try:
        logger.info(f"Generating content for topic: {topic}")
        
        # Validate input
        if not topic:
            st.error("❌ Please enter a topic!")
            return None, 0
        elif not topic.strip():
            st.error("❌ Topic cannot be empty!")
            return None, 0
        
        status_text.write("⏳ Starting workflow...")
        time.sleep(0.5)
        
        start_time = time.time()
        
        # Run workflow
        try:
            final_state = run_workflow(
                topic=topic,
                content_type=content_type,
                target_audience=target_audience
            )
        except Exception as workflow_error:
            logger.error(f"Workflow error: {workflow_error}")
            st.error("Workflow execution failed. Please try again.")
            return None, 0
        
        duration = time.time() - start_time
        
        # Update progress through stages
        for stage, (message, progress) in WORKFLOW_STAGES.items():
            status_text.write(message)
            progress_bar.progress(progress)
            time.sleep(0.2)
        
        # Validate final state
        if not final_state:
            st.error("❌ No content state returned")
            return None, 0
        
        # Ensure metadata exists with safe defaults
        if not final_state.get('metadata'):
            final_state['metadata'] = {
                'word_count': len(final_state.get('final_content', '').split()),
                'sources_used': 0,
                'confidence_score': 75,
                'revision_made': False
            }
        
        # Validate confidence_score is a valid number
        confidence = final_state['metadata'].get('confidence_score', 75)
        if not isinstance(confidence, (int, float)):
            final_state['metadata']['confidence_score'] = 75
        
        # Ensure all required fields exist
        if 'final_content' not in final_state:
            st.error("❌ No content generated")
            return None, 0
        
        return final_state, duration
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        st.error(f"Invalid input: {str(e)}")
        return None, 0
    except ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        st.error("Workflow connection failed. Please try again.")
        return None, 0
    except Exception as e:
        logger.error(f"Unexpected generation error: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")
        return None, 0

def display_content_metrics(metadata: Dict):
    """Display content metadata in metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Word Count", f"{metadata.get('word_count', 0)}")
    with col2:
        st.metric("📚 Sources", f"{metadata.get('sources_used', 0)}")
    with col3:
        st.metric("✅ Confidence", f"{metadata.get('confidence_score', 0)}%")
    with col4:
        st.metric("🔄 Revised", "Yes" if metadata.get('revision_made') else "No")

def display_citations(citations: List[Dict]):
    """Display citations in a formatted way."""
    if not citations:
        return
    
    st.markdown("### 📚 Sources")
    for idx, citation in enumerate(citations, 1):
        st.markdown(f"{idx}. [{citation.get('source', 'Unknown')}]({citation.get('url', '#')})")

def display_generated_content(final_state: Dict, db, duration: float):
    """Display generated content with all components."""
    st.markdown("""
    <div class="success-box">
    <h4>✓ Content Generated Successfully!</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.success(f"Generated in {duration:.2f} seconds")
    st.write("---")
    
    # Display metrics with safe defaults
    metadata = final_state.get('metadata', {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📝 Word Count", f"{metadata.get('word_count', 0)}")
    with col2:
        st.metric("📚 Sources", f"{metadata.get('sources_used', 0)}")
    with col3:
        confidence = metadata.get('confidence_score', 75)
        st.metric("✅ Confidence", f"{confidence}%")
    with col4:
        st.metric("🔄 Revised", "Yes" if metadata.get('revision_made') else "No")
    
    st.write("---")
    
    # Display content
    st.markdown("### 📄 Generated Content")
    content_text = final_state.get('final_content', 'No content generated')
    st.markdown(content_text)
    
    # Display citations
    if final_state.get('citations'):
        st.write("---")
        st.markdown("### 📚 Sources")
        for idx, citation in enumerate(final_state['citations'], 1):
            source_text = citation.get('source', 'Unknown')
            source_url = citation.get('url', '#')
            st.markdown(f"{idx}. [{source_text}]({source_url})")
    
    st.write("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="⬇️ Download as Text",
            data=final_state.get('final_content', ''),
            file_name=f"{final_state.get('topic', 'content').replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        st.code(final_state.get('final_content', ''), language="markdown")
    
    with col3:
        if st.button("🔄 Generate Another", use_container_width=True):
            st.rerun()

def get_dashboard_stats(db) -> tuple:
    """Get dashboard statistics efficiently."""
    try:
        all_content = db.get_all_content(limit=1000)
        
        total_generated = len(all_content)
        
        avg_score = (
            sum(c['confidence_score'] for c in all_content) / len(all_content)
            if all_content else 0
        )
        
        total_words = (
            sum(c['word_count'] for c in all_content)
            if all_content else 0
        )
        
        return total_generated, avg_score, total_words, all_content
    except Exception as e:
        st.error(f"Error fetching statistics: {str(e)}")
        get_logger().error(f"Stats error: {str(e)}")
        return 0, 0, 0, []

# ============================================================================
# PAGE: HOME
# ============================================================================
def page_home():
    """Home page with statistics and overview."""
    st.title("🚀 Content Research & Writing Assistant")
    st.write("---")
    
    db = safe_get_db()
    if not db:
        return
    
    # Get statistics
    total_generated, avg_score, total_words, all_content = get_dashboard_stats(db)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Generated",
            total_generated,
            "pieces"
        )
    
    with col2:
        st.metric(
            "Avg Confidence",
            f"{avg_score:.1f}%",
            "+5%" if avg_score > 80 else "-5%"
        )
    
    with col3:
        st.metric(
            "Total Words",
            f"{total_words:,}",
            "generated"
        )
    
    st.write("---")
    
    st.markdown("""
    ### Welcome! 👋
    
    This is an AI-powered **Content Research & Writing Assistant** that helps you generate 
    high-quality content in minutes. Here's what you can do:
    
    #### ✨ Features:
    - 🔍 **Automated Research**: Gather information from multiple web sources
    - 📝 **Intelligent Writing**: Generate professional, engaging content
    - ✅ **Fact-Checking**: Verify accuracy and provide revisions
    - 📚 **Citation Management**: Automatic source attribution
    - 💾 **Content History**: Save and retrieve previous work
    - ⚡ **Fast Generation**: Get results in seconds
    
    #### 📋 Supported Content Types:
    - **Blog Post**: 600-1000 words, engaging tone
    - **Article**: 800-1500 words, professional tone
    - **Social Media**: 50-280 characters, casual tone
    
    #### 🚀 Get Started:
    Click **"✍️ Generate Content"** from the sidebar to create your first piece!
    """)
    
    st.write("---")
    st.markdown("### 📊 Recent Generations")
    
    recent = db.get_all_content(limit=5)
    if recent:
        for idx, content in enumerate(recent, 1):
            with st.expander(
                f"{idx}. {content.get('topic', 'Untitled')} "
                f"({format_content_type(content.get('content_type', 'unknown'))})"
            ):
                st.write(f"**Created**: {content.get('created_at', 'N/A')}")
                st.write(f"**Word Count**: {content.get('word_count', 0)}")
                st.write(f"**Confidence**: {content.get('confidence_score', 0)}%")
                
                if st.button(
                    "View Full Content",
                    key=f"view_{content.get('id')}"
                ):
                    st.session_state.current_content_id = content.get('id')
                    st.switch_page("pages/view_content.py")
    else:
        st.info("No content generated yet. Start by creating your first piece!")

# ============================================================================
# PAGE: GENERATE CONTENT
# ============================================================================
def page_generate_content():
    """Generate new content page."""
    st.title("✍️ Generate Content")
    st.write("---")
    
    db = safe_get_db()
    if not db:
        return
    
    # Input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "📌 Topic",
            placeholder="Enter the topic you want to write about...",
            help="Be specific for better results",
            max_chars=200
        )
    
    with col2:
        content_type = st.selectbox(
            "📄 Content Type",
            list(CONTENT_TYPES.keys()),
            format_func=format_content_type
        )
    
    target_audience = st.text_input(
        "👥 Target Audience",
        placeholder="e.g., Software developers, Beginners, Tech enthusiasts",
        help="Optional: Helps tailor the content",
        max_chars=150
    )
    
    st.write("---")
    st.info(get_guideline(content_type))
    st.write("---")
    
    # Generate button
    if st.button("🚀 Generate Content", use_container_width=True, type="primary"):
        if not topic.strip():
            st.error("❌ Please enter a topic!")
        else:
            # Create progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Run content generation
            final_state, duration = run_content_generation(
                topic=topic,
                content_type=content_type,
                target_audience=target_audience,
                progress_bar=progress_bar,
                status_text=status_text
            )
            
            # Handle results
            if final_state and final_state.get('final_content'):
                # Save to database
                content_id = None
                try:
                    content_id = db.save_content(final_state)
                    st.session_state.current_content_id = content_id
                    st.session_state.generated_content = final_state
                except Exception as db_error:
                    get_logger().error(f"Database error: {db_error}")
                    st.warning("⚠️ Content generated but could not save to database")
                
                # Clear progress indicators
                progress_bar.progress(1.0)
                status_text.empty()
                
                # Display generated content
                display_generated_content(final_state, db, duration)
                
                # Show save status
                st.write("---")
                if content_id:
                    st.success(f"✓ Content saved with ID: {content_id}")
                else:
                    st.warning("⚠️ Content was not saved to database")
            
            elif final_state is None:
                progress_bar.empty()
                status_text.empty()
                # Error message already shown in run_content_generation
            else:
                progress_bar.empty()
                status_text.empty()
                error_msg = final_state.get('error_message', 'Unknown error') if final_state else 'No state returned'
                st.error(f"❌ Content generation failed: {error_msg}")

# ============================================================================
# PAGE: HISTORY
# ============================================================================
def page_history():
    """Content history and management page."""
    st.title("📚 Content History")
    st.write("---")
    
    db = safe_get_db()
    if not db:
        return
    
    try:
        # Get all content
        all_content = db.get_all_content(limit=1000)
        
        if not all_content:
            st.info("No content generated yet.")
            return
        
        # Search and filter
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search by topic", "")
        
        with col2:
            filter_type = st.selectbox(
                "Filter by type",
                ["All"] + list(CONTENT_TYPES.keys()),
                format_func=lambda x: "All Types" if x == "All" else format_content_type(x)
            )
        
        # Filter content
        filtered_content = all_content
        
        if search_query.strip():
            filtered_content = [
                c for c in filtered_content
                if search_query.lower() in c.get('topic', '').lower()
            ]
        
        if filter_type != "All":
            filtered_content = [
                c for c in filtered_content
                if c.get('content_type') == filter_type
            ]
        
        st.write(f"Found **{len(filtered_content)}** items")
        st.write("---")
        
        if filtered_content:
            # Create DataFrame for display
            df_data = [
                {
                    'ID': c.get('id', ''),
                    'Topic': c.get('topic', 'Untitled'),
                    'Type': format_content_type(c.get('content_type', 'unknown')).upper(),
                    'Words': c.get('word_count', 0),
                    'Confidence': f"{c.get('confidence_score', 0)}%",
                    'Created': c.get('created_at', 'N/A')[:10]
                }
                for c in filtered_content
            ]
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.write("---")
            
            # Detailed view
            st.markdown("### 🔎 View Details")
            selected_id = st.selectbox(
                "Select content to view",
                [c.get('id') for c in filtered_content],
                format_func=lambda x: next(
                    (c.get('topic', 'Unknown') for c in filtered_content if c.get('id') == x),
                    "Unknown"
                )
            )
            
            if selected_id:
                content = db.get_content(selected_id)
                
                if content:
                    st.markdown(f"### {content.get('topic', 'Untitled')}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Type", format_content_type(content.get('content_type', 'unknown')).upper())
                    with col2:
                        st.metric("Words", content.get('word_count', 0))
                    with col3:
                        st.metric("Sources", content.get('sources_count', 0))
                    with col4:
                        st.metric("Confidence", f"{content.get('confidence_score', 0)}%")
                    
                    st.write("---")
                    
                    st.markdown("#### 📄 Content")
                    st.markdown(content.get('final_content', ''))
                    
                    # Display citations
                    display_citations(content.get('citations', []))
                    
                    st.write("---")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Download",
                            data=content.get('final_content', ''),
                            file_name=f"{content.get('topic', 'content').replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("🗑️ Delete", use_container_width=True, key="delete_btn"):
                            try:
                                db.delete_content(selected_id)
                                st.success("✓ Content deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {str(e)}")
                                get_logger().error(f"Delete error: {str(e)}")
                    
                    with col3:
                        st.markdown(f"**Created**: {content.get('created_at', 'N/A')}")
    
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")
        get_logger().error(f"History page error: {str(e)}")

# ============================================================================
# PAGE: ABOUT
# ============================================================================
def page_about():
    """About page with application information."""
    st.title("ℹ️ About This Application")
    st.write("---")
    
    st.markdown(f"""
    ## 🎯 {APP_NAME}
    
    An AI-powered application that generates high-quality, researched content automatically.
    
    ### 🏗️ Architecture
    
    - **Framework**: LangGraph (Multi-Agent Orchestration)
    - **LLM**: Groq (Fast & Efficient)
    - **Web Search**: Tavily API
    - **Frontend**: Streamlit
    - **Database**: SQLite
    
    ### 📊 Workflow
    
    1. **🔍 Research**: Web search for relevant information
    2. **📊 Analysis**: Extract key points and organize insights
    3. **✍️ Writing**: Generate engaging content
    4. **✅ Fact-Checking**: Verify accuracy and claims
    5. **🔄 Revision**: Auto-improve based on fact-check results
    6. **🎯 Finalization**: Format and prepare final output
    
    ### 📈 Statistics
    
    - **Processing Time**: 30-60 seconds per article
    - **Source Quality**: Multiple reliable web sources
    - **Accuracy Rate**: 85-95% confidence score
    - **Content Types**: Blog, Article, Social Media
    
    ### 🛠️ Technology Stack
    
    - **Backend**: Python 3.11+
    - **LLM Framework**: LangChain
    - **Agent Orchestration**: LangGraph
    - **LLM Provider**: Groq
    - **Search Provider**: Tavily
    - **Web Framework**: Streamlit
    - **Database**: SQLite3
    - **Deployment**: Streamlit Cloud, Docker
    
    ### 📝 Version
    
    **{APP_VERSION}** - Latest Release
    
    ### ✨ Key Features
    
    ✅ Automated research with web search  
    ✅ AI-powered content generation  
    ✅ Automatic fact-checking and revision  
    ✅ Citation management  
    ✅ Multiple content formats  
    ✅ Content history and management  
    ✅ Fast processing (30-60 seconds)  
    ✅ Professional quality output  
    
    ### 🚀 Getting Started
    
    1. Enter a topic
    2. Select content type (Blog, Article, Social)
    3. Click "Generate Content"
    4. Review and download the result
    
    ### 📞 Support
    
    For issues or feature requests, please contact the development team.
    
    ### 🔒 Data Privacy
    
    - Your content is stored locally in the database
    - API keys are securely managed
    - No data is shared with third parties beyond API providers
    
    ---
    
    **Built with ❤️ using AI and LangGraph**
    """)

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================
st.sidebar.title("⚙️ Configuration")
st.sidebar.write("---")

# Validate API keys
is_valid, validation_message = validate_api_keys()
if is_valid:
    st.sidebar.success(f"✓ {validation_message}")
else:
    st.sidebar.error(f"❌ {validation_message}")
    st.stop()

# Navigation
with st.sidebar:
    page = option_menu(
        "Navigation",
        ["🏠 Home", "✍️ Generate Content", "📚 History", "ℹ️ About"],
        icons=["house", "pencil-square", "clock-history", "info-circle"],
        menu_icon="cast",
        default_index=0
    )

# ============================================================================
# PAGE ROUTING
# ============================================================================
if page == "🏠 Home":
    page_home()
elif page == "✍️ Generate Content":
    page_generate_content()
elif page == "📚 History":
    page_history()
elif page == "ℹ️ About":
    page_about()

# ============================================================================
# FOOTER
# ============================================================================
st.write("---")
st.markdown(f"""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
    <p>{APP_NAME} {APP_VERSION} | Powered by Groq & Tavily</p>
</div>
""", unsafe_allow_html=True)