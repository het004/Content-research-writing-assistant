import streamlit as st
from streamlit_option_menu import option_menu
import time
from datetime import datetime
from config.settings import settings
from workflows.graph import run_workflow
from database.models import ContentModel
from utilis.logger import WorkflowLogger

import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Content Research & Writing Assistant",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'current_content_id' not in st.session_state:
    st.session_state.current_content_id = None

# Initialize managers
db = ContentModel()
logger = WorkflowLogger()
#cache = CacheManager()

# Sidebar configuration
st.sidebar.title("⚙️ Configuration")
st.sidebar.write("---")

# Validate API keys
try:
    settings.validate()
    st.sidebar.success("✓ API Keys Configured")
except ValueError as e:
    st.sidebar.error(f"❌ Configuration Error: {e}")
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
# PAGE: HOME
# ============================================================================
if page == "🏠 Home":
    st.title("🚀 Content Research & Writing Assistant")
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Generated",
            len(db.get_all_content(limit=1000)),
            "pieces"
        )
    
    with col2:
        all_content = db.get_all_content(limit=1000)
        avg_score = sum([c['confidence_score'] for c in all_content]) / len(all_content) if all_content else 0
        st.metric(
            "Avg Confidence",
            f"{avg_score:.1f}%",
            "+5%" if avg_score > 80 else "-5%"
        )
    
    with col3:
        all_content = db.get_all_content(limit=1000)
        total_words = sum([c['word_count'] for c in all_content]) if all_content else 0
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
            with st.expander(f"{idx}. {content['topic']} ({content['content_type']})"):
                st.write(f"**Created**: {content['created_at']}")
                st.write(f"**Word Count**: {content['word_count']}")
                st.write(f"**Confidence**: {content['confidence_score']}%")
                if st.button(f"View Full Content", key=f"view_{content['id']}"):
                    st.session_state.current_content_id = content['id']
                    st.switch_page("pages/view_content.py")
    else:
        st.info("No content generated yet. Start by creating your first piece!")


# ============================================================================
# PAGE: GENERATE CONTENT
# ============================================================================
elif page == "✍️ Generate Content":
    st.title("✍️ Generate Content")
    st.write("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_input(
            "📌 Topic",
            placeholder="Enter the topic you want to write about...",
            help="Be specific for better results"
        )
    
    with col2:
        content_type = st.selectbox(
            "📄 Content Type",
            ["blog", "article", "social"],
            format_func=lambda x: {
                "blog": "Blog Post",
                "article": "Article",
                "social": "Social Media"
            }.get(x)
        )
    
    target_audience = st.text_input(
        "👥 Target Audience",
        placeholder="e.g., Software developers, Beginners, Tech enthusiasts",
        help="Optional: Helps tailor the content"
    )
    
    st.write("---")
    
    # Display content type guidelines
    guidelines = {
        "blog": "💡 **Blog Post**: 600-1000 words, engaging and accessible tone",
        "article": "📰 **Article**: 800-1500 words, formal and professional tone",
        "social": "📱 **Social Media**: 50-280 characters, concise and catchy"
    }
    
    st.info(guidelines.get(content_type, ""))
    
    st.write("---")
    
    # Generate button with progress tracking
    if st.button("🚀 Generate Content", use_container_width=True, type="primary"):
        if not topic:
            st.error("❌ Please enter a topic!")
        else:
            # Create progress bar and status updates
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            stages = {
                "research": ("🔍 Researching...", 0.16),
                "analysis": ("📊 Analyzing...", 0.32),
                "writing": ("✍️ Writing...", 0.48),
                "fact_checking": ("✅ Fact-Checking...", 0.64),
                "revision": ("🔄 Revising...", 0.80),
                "finalization": ("🎯 Finalizing...", 1.0)
            }
            
            try:
                status_text.write("⏳ Starting workflow...")
                time.sleep(0.5)
                
                # Run workflow with simulated progress
                start_time = time.time()
                final_state = run_workflow(
                    topic=topic,
                    content_type=content_type,
                    target_audience=target_audience
                )
                duration = time.time() - start_time
                
                # Update progress
                for stage, (message, progress) in stages.items():
                    status_text.write(message)
                    progress_bar.progress(progress)
                    time.sleep(0.2)
                
                # Check if successful
                if final_state.get('final_content'):
                    # Save to database
                    content_id = db.save_content(final_state)
                    st.session_state.current_content_id = content_id
                    st.session_state.generated_content = final_state
                    
                    # Success message
                    progress_bar.progress(1.0)
                    status_text.empty()
                    
                    st.markdown("""
                    <div class="success-box">
                    <h4>✓ Content Generated Successfully!</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success(f"Generated in {duration:.2f} seconds")
                    
                    # Display results
                    st.write("---")
                    
                    # Metadata
                    metadata = final_state.get('metadata', {})
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📝 Word Count", f"{metadata.get('word_count', 0)}")
                    with col2:
                        st.metric("📚 Sources", f"{metadata.get('sources_used', 0)}")
                    with col3:
                        st.metric("✅ Confidence", f"{metadata.get('confidence_score', 0)}%")
                    with col4:
                        st.metric("🔄 Revised", "Yes" if metadata.get('revision_made') else "No")
                    
                    st.write("---")
                    
                    # Content display
                    st.markdown("### 📄 Generated Content")
                    st.markdown(final_state.get('final_content', ''))
                    
                    st.write("---")
                    
                    # Citations
                    if final_state.get('citations'):
                        st.markdown("### 📚 Sources")
                        for citation in final_state['citations']:
                            st.markdown(f"- [{citation['source']}]({citation['url']})")
                    
                    st.write("---")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Download as Text",
                            data=final_state.get('final_content', ''),
                            file_name=f"{topic.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
                    
                    with col2:
                        # Copy to clipboard
                        st.markdown(
                            f'<button onclick="navigator.clipboard.writeText(\'{final_state.get("final_content", "").replace(chr(39), "\\\\'")}\')" style="width: 100%; padding: 0.5rem; border-radius: 0.25rem; border: 1px solid #ddd; background-color: #f0f2f6; cursor: pointer;">📋 Copy to Clipboard</button>',
                            unsafe_allow_html=True
                        )
                    
                    with col3:
                        if st.button("💾 Save to Database", use_container_width=True):
                            st.success(f"✓ Saved with ID: {content_id}")
                
                else:
                    st.error(f"❌ Content generation failed: {final_state.get('error_message')}")
            
            except Exception as e:
                status_text.empty()
                progress_bar.empty()
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Generation error: {str(e)}")


# ============================================================================
# PAGE: HISTORY
# ============================================================================
elif page == "📚 History":
    st.title("📚 Content History")
    st.write("---")
    
    # Get all content
    all_content = db.get_all_content(limit=100)
    
    if not all_content:
        st.info("No content generated yet.")
    else:
        # Search and filter
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search by topic", "")
        
        with col2:
            filter_type = st.selectbox(
                "Filter by type",
                ["All", "blog", "article", "social"]
            )
        
        # Filter content
        filtered_content = all_content
        
        if search_query:
            filtered_content = [
                c for c in filtered_content
                if search_query.lower() in c['topic'].lower()
            ]
        
        if filter_type != "All":
            filtered_content = [
                c for c in filtered_content
                if c['content_type'] == filter_type
            ]
        
        st.write(f"Found **{len(filtered_content)}** items")
        st.write("---")
        
        # Display as table
        if filtered_content:
            # Create DataFrame
            df = pd.DataFrame([
                {
                    'ID': c['id'],
                    'Topic': c['topic'],
                    'Type': c['content_type'].upper(),
                    'Words': c['word_count'],
                    'Confidence': f"{c['confidence_score']}%",
                    'Created': c['created_at'][:10]
                }
                for c in filtered_content
            ])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.write("---")
            
            # Detailed view
            st.markdown("### 🔎 View Details")
            selected_id = st.selectbox(
                "Select content to view",
                [c['id'] for c in filtered_content],
                format_func=lambda x: next(
                    (c['topic'] for c in filtered_content if c['id'] == x),
                    "Unknown"
                )
            )
            
            if selected_id:
                content = db.get_content(selected_id)
                
                if content:
                    st.markdown(f"### {content['topic']}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Type", content['content_type'].upper())
                    with col2:
                        st.metric("Words", content['word_count'])
                    with col3:
                        st.metric("Sources", content['sources_count'])
                    with col4:
                        st.metric("Confidence", f"{content['confidence_score']}%")
                    
                    st.write("---")
                    
                    st.markdown("#### 📄 Content")
                    st.markdown(content['final_content'])
                    
                    if content['citations']:
                        st.write("---")
                        st.markdown("#### 📚 Citations")
                        for citation in content['citations']:
                            st.markdown(f"- [{citation['source']}]({citation['url']})")
                    
                    st.write("---")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            label="⬇️ Download",
                            data=content['final_content'],
                            file_name=f"{content['topic'].replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        if st.button("🗑️ Delete", use_container_width=True):
                            db.delete_content(selected_id)
                            st.success("✓ Content deleted!")
                            st.rerun()
                    
                    with col3:
                        st.markdown(f"**Created**: {content['created_at']}")


# ============================================================================
# PAGE: ABOUT
# ============================================================================
elif page == "ℹ️ About":
    st.title("ℹ️ About This Application")
    st.write("---")
    
    st.markdown("""
    ## 🎯 Content Research & Writing Assistant
    
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
    
    **v1.0.0** - Initial Release
    
    ### 👨‍💻 Features
    
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
    
    ---
    
    **Built with ❤️ using AI and LangGraph**
    """)


# ============================================================================
# Footer
# ============================================================================
st.write("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.85rem;">
    <p>Content Research & Writing Assistant v1.0.0 | Powered by Groq & Tavily</p>
</div>
""", unsafe_allow_html=True)











