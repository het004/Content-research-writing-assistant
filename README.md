# 📝 Content Research & Writing Assistant

An **AI-powered multi-agent system** that generates high-quality, researched content automatically. Powered by LangGraph, Groq, and Streamlit.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-Production%20Ready-success)

---

## 🌟 Features

- 🔍 **Automated Research**: Gathers information from multiple web sources using Tavily API
- 📝 **Intelligent Writing**: Generates professional, engaging content using Groq LLM
- ✅ **Fact-Checking**: Automatically verifies accuracy and provides revisions
- 📚 **Citation Management**: Collects and formats source citations automatically
- 💾 **Content History**: Save and retrieve previously generated content from SQLite database
- ⚡ **Fast Generation**: Get high-quality content in 30-60 seconds
- 🎨 **Beautiful UI**: User-friendly Streamlit web interface
- 📊 **Multi-format Support**: Blog posts, articles, and social media content
- 📈 **Tracking & Analytics**: Monitor confidence scores, word counts, and sources
- 🔄 **Auto-Revision**: Content improvement based on fact-checking results

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Deployment](#-deployment)
- [Project Structure](#-project-structure)
- [API Integration](#-api-integration)
- [Database Schema](#-database-schema)
- [Workflow](#-workflow)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | Groq | Fast language model inference |
| **Web Search** | Tavily API | Real-time information retrieval |
| **Orchestration** | LangGraph | Multi-agent workflow management |
| **Framework** | LangChain | LLM application framework |
| **Frontend** | Streamlit | Web UI and deployment |
| **Database** | SQLite | Content persistence |
| **Language** | Python 3.11+ | Primary language |
| **Environment** | python-dotenv | Configuration management |

---

## 🏗 Architecture

The application uses a **multi-agent architecture** with the following components:

```
┌─────────────────────────────────────────────────────────┐
│                    STREAMLIT UI                         │
│         (Home, Generate, History, About)               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   LANGGRAPH WORKFLOW                    │
│  ┌────────────────────────────────────────────────┐   │
│  │ Research Agent → Analysis → Writing → Fact     │   │
│  │ Checking → Revision (optional) → Finalization  │   │
│  └────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐  ┌────▼────┐  ┌──────▼──────┐
   │ Groq    │  │ Tavily  │  │ SQLite      │
   │ LLM     │  │ Search  │  │ Database    │
   └─────────┘  └─────────┘  └─────────────┘
```

---

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/content-research-assistant.git
cd content-research-assistant
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements_streamlit.txt
```

Or install all dependencies including optional ones:

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
cp .env.example .env
```

Edit `.env` and add your API keys:

```
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
CONTENT_TYPE=blog
LOG_LEVEL=INFO
DEBUG=False
```

### Step 5: Verify Installation

```bash
python test_setup.py
```

You should see:
```
✓ All required API keys validated successfully
```

---

## 🔑 Configuration

### Getting API Keys

#### Groq API Key
1. Visit https://console.groq.com/
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy the key to your `.env` file

**Recommended Model**: `mixtral-8x7b-32768` (fastest and best quality)

#### Tavily API Key
1. Visit https://tavily.com/
2. Sign up
3. Copy API key from dashboard
4. Add to `.env` file

**Free Tier**: 1,000 API calls/month (sufficient for testing)

### Advanced Configuration

Edit `.streamlit/config.toml` to customize:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#F5F5F5"
textColor = "#2C3E50"

[client]
showErrorDetails = true
toolbarMode = "viewer"
```

---

## 🚀 Usage

### Quick Start

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run the application
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### Using the Application

#### 1. **Generate Content** (Main Feature)
   - Navigate to "✍️ Generate Content" tab
   - Enter a topic (e.g., "Machine Learning in Healthcare")
   - Select content type:
     - **Blog**: 600-1000 words, engaging tone
     - **Article**: 800-1500 words, professional tone
     - **Social**: 50-280 characters, casual tone
   - (Optional) Enter target audience
   - Click "🚀 Generate Content"
   - Watch real-time progress
   - Download or copy the generated content

#### 2. **View History**
   - Navigate to "📚 History" tab
   - Search by topic
   - Filter by content type
   - Click on any item to view full details
   - Download or delete content as needed

#### 3. **Home Dashboard**
   - View statistics:
     - Total pieces generated
     - Average confidence score
     - Total words generated
   - See recent generations
   - Quick access to features

#### 4. **About**
   - Learn about the application
   - View technology stack
   - Understand the workflow

---

## 📦 Deployment

### Option 1: Streamlit Cloud (Recommended - Free!)

**Steps:**

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Connect your GitHub repo
   - Select branch and file: `app.py`
   - Click "Deploy"

3. **Add Secrets**
   - In Streamlit Cloud dashboard
   - Go to "Advanced settings"
   - Add secrets:
     ```
     GROQ_API_KEY = "your_key_here"
     TAVILY_API_KEY = "your_key_here"
     ```

4. **Done!** Your app is live 🎉

### Option 2: Docker

**Build Image:**
```bash
docker build -t content-assistant:latest .
```

**Run Container:**
```bash
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  content-assistant:latest
```

**Or with Docker Compose:**
```bash
docker-compose up
```

### Option 3: Self-Hosted Server

**On Ubuntu/Debian:**

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install python3.11 python3-pip git

# Clone repository
git clone https://github.com/yourusername/content-research-assistant.git
cd content-research-assistant

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements_streamlit.txt

# Create .env file with your keys
nano .env

# Run application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Access at**: `http://your-server-ip:8501`

### Option 4: Using Gunicorn + Nginx (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --workers 4 --worker-class sync --timeout 120 -b 0.0.0.0:8000 "streamlit.cli:_main_run_app" app.py
```

---

## 📁 Project Structure

```
content-research-assistant/
│
├── 📄 app.py                           # Main Streamlit application
├── 📄 README.md                        # This file
├── 📄 requirements.txt                 # All dependencies
├── 📄 requirements_streamlit.txt       # Streamlit-specific dependencies
├── 📄 .env.example                     # Environment variables template
├── 📄 .gitignore                       # Git ignore rules
│
├── 📁 config/
│   ├── __init__.py
│   ├── settings.py                     # Configuration management
│   └── workflow_config.yaml            # (Generated) Workflow settings
│
├── 📁 database/
│   ├── __init__.py
│   └── models.py                       # SQLite database models
│
├── 📁 workflow/
│   ├── __init__.py
│   ├── state.py                        # Workflow state schema
│   └── graph.py                        # LangGraph workflow definition
│
├── 📁 agents/
│   ├── __init__.py
│   ├── research_agent.py               # Web research agent
│   ├── analysis_agent.py               # Content analysis agent
│   ├── writing_agent.py                # Content writing agent
│   └── fact_checking_agent.py          # Fact verification agent
│
├── 📁 tools/
│   ├── __init__.py
│   ├── web_search.py                   # Tavily search integration
│   ├── summarizer.py                   # Text summarization
│   └── fact_checker.py                 # Fact checking logic
│
├── 📁 utils/
│   ├── __init__.py
│   ├── logger.py                       # Logging system
│   └── cache.py                        # Caching utilities
│
├── 📁 tests/
│   ├── test_api.py                     # API endpoint tests
│   └── test_integration.py             # Workflow integration tests
│
├── 📁 .streamlit/
│   └── config.toml                     # Streamlit configuration
│
├── 📁 docker/
│   ├── Dockerfile                      # Docker image definition
│   └── docker-compose.yml              # Docker compose configuration
│
├── 📁 logs/                            # (Auto-created) Log files
├── 📁 data/                            # (Auto-created) Database files
│
├── 🐚 run_streamlit.sh                 # Linux/Mac startup script
└── 🐚 run_streamlit.bat                # Windows startup script
```

---

## 🔌 API Integration

### Groq API

**Model**: `mixtral-8x7b-32768`

**Features**:
- Super fast inference (LPU-based)
- Excellent for multi-agent workflows
- Cost-effective
- Free tier available

**Usage in Code**:
```python
from langchain_groq import ChatGroq
from config.settings import settings

llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0.7
)
```

### Tavily API

**Purpose**: Real-time web search

**Features**:
- Optimized for AI agents
- Returns structured results
- Includes direct answers
- Free tier: 1,000 calls/month

**Usage in Code**:
```python
from tools.web_search import WebSearchTool

search_tool = WebSearchTool()
results = search_tool.search("topic query", max_results=5)
```

---

## 💾 Database Schema

### Table: `generated_content`

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER | Primary key |
| topic | TEXT | Content topic |
| content_type | TEXT | blog/article/social |
| target_audience | TEXT | Intended audience |
| final_content | TEXT | Generated content |
| word_count | INTEGER | Number of words |
| sources_count | INTEGER | Number of sources |
| confidence_score | INTEGER | Accuracy confidence (0-100) |
| revision_made | BOOLEAN | Was content revised? |
| metadata | JSON | Additional metadata |
| citations | JSON | Source citations |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

### Table: `execution_logs`

| Column | Type | Purpose |
|--------|------|---------|
| id | INTEGER | Primary key |
| content_id | INTEGER | Reference to generated_content |
| stage | TEXT | Workflow stage name |
| status | TEXT | Stage status |
| message | TEXT | Stage message |
| duration_seconds | FLOAT | Execution duration |
| created_at | TIMESTAMP | Log time |

---

## 🔄 Workflow

The system follows a 6-stage workflow:

### Stage 1: 🔍 Research
- **Agent**: ResearchAgent
- **Action**: Web search for relevant information
- **Output**: research_data (sources, summaries, URLs)
- **Time**: 5-10 seconds

### Stage 2: 📊 Analysis
- **Agent**: AnalysisAgent
- **Action**: Extract key points and organize insights
- **Output**: analysis (key_points, structure, themes)
- **Time**: 3-5 seconds

### Stage 3: ✍️ Writing
- **Agent**: WritingAgent
- **Action**: Generate engaging content
- **Output**: draft (initial content)
- **Time**: 5-10 seconds

### Stage 4: ✅ Fact-Checking
- **Agent**: FactCheckingAgent
- **Action**: Verify accuracy and claims
- **Output**: fact_check_results (issues, confidence)
- **Time**: 3-5 seconds

### Stage 5: 🔄 Revision (Conditional)
- **Agent**: RevisionAgent
- **Action**: Improve content based on fact-check feedback
- **Output**: revised_draft
- **Time**: 3-5 seconds (only if needed)
- **Triggers**: If fact-checking finds issues

### Stage 6: 🎯 Finalization
- **Agent**: FinalizationAgent
- **Action**: Format, add metadata, collect citations
- **Output**: final_content, metadata, citations
- **Time**: 1-2 seconds

**Total Time**: 30-60 seconds per content piece

---

## 🐛 Troubleshooting

### Issue: "API Key not found"
**Solution**:
```bash
# Check .env file exists
ls -la .env

# Verify keys are set
cat .env

# If missing, create/update .env with your keys
```

### Issue: "Tavily API connection error"
**Solution**:
1. Check internet connection
2. Verify API key is correct
3. Check Tavily API status
4. Try again in a few moments

### Issue: "Streamlit app not opening"
**Solution**:
```bash
# Try specific port
streamlit run app.py --server.port 8502

# Or disable SSL
streamlit run app.py --client.showErrorDetails=true
```

### Issue: "Database locked"
**Solution**:
```bash
# Remove old database
rm data/content.db

# Restart app
streamlit run app.py
```

### Issue: "ModuleNotFoundError"
**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements_streamlit.txt --upgrade

# Or reinstall everything
pip install -r requirements.txt --upgrade
```

### Issue: Content generation takes too long
**Potential causes**:
- Slow internet connection
- Groq API overload
- Large topic requiring extensive research
- Try simpler topics first

---

## 🧪 Testing

### Run Tests

```bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/ --cov=. -v
```

### Manual Testing

```bash
# Test agents individually
python -m agents.research_agent

# Test workflow
python test_setup.py

# Test Streamlit
streamlit run app.py
```

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| Average Generation Time | 30-60 seconds |
| Average Confidence Score | 85-95% |
| Average Word Count | 600-1200 words |
| API Calls per Generation | 5-10 |
| Database Query Time | <100ms |
| UI Load Time | <2 seconds |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Style
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- **LangGraph**: Multi-agent orchestration
- **Groq**: Fast LLM inference
- **Tavily**: Intelligent web search
- **Streamlit**: Beautiful web framework
- **LangChain**: LLM framework

---

## 📞 Support

### Getting Help

1. **Check Troubleshooting Section**: Common issues and solutions
2. **Read Logs**: Check `logs/` directory for detailed error messages
3. **GitHub Issues**: Report bugs or request features
4. **Documentation**: Review docstrings in code

### Common Questions

**Q: Can I use a different LLM?**
A: Yes! Modify `config/settings.py` to use OpenAI, Anthropic, or other providers.

**Q: Can I customize the workflow?**
A: Yes! Edit `workflow/graph.py` to add/remove/modify agents.

**Q: How do I reduce API costs?**
A: Enable caching, reduce search results, use smaller models.

**Q: Can I deploy on my own server?**
A: Yes! Use Docker or follow the self-hosted guide above.

---

## 📈 Roadmap

### Future Enhancements
- [ ] Multi-language support
- [ ] PDF export functionality
- [ ] User authentication & team collaboration
- [ ] Advanced analytics dashboard
- [ ] Email integration for content delivery
- [ ] SEO optimization suggestions
- [ ] Template system for different industries
- [ ] Batch content generation
- [ ] API endpoint access
- [ ] Mobile app

---

## 📜 Version History

### v1.0.0 (Current)
- ✅ Core multi-agent workflow
- ✅ Streamlit web interface
- ✅ Database persistence
- ✅ Fact-checking and auto-revision
- ✅ Content history management

### v0.1.0 (Alpha)
- Initial project setup
- Agent development
- LangGraph integration

---

## 🎓 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Groq API Documentation](https://console.groq.com/docs)
- [Tavily API Documentation](https://tavily.com/docs)

---

## 📧 Contact

For questions or suggestions, please open an issue or contact the development team.

---

<div align="center">

**Built with ❤️ using LangGraph, Groq, and Streamlit**

⭐ If you found this helpful, please consider giving it a star!

</div>