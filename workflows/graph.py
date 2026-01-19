from langgraph.graph import StateGraph, END
from workflows.state import ContentResearchState
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writing_agent import WritingAgent
from agents.fact_checking_agent import FactCheckingAgent
from langchain_groq import ChatGroq
from config.settings import settings

# Initialize agents
research_agent = ResearchAgent()
analysis_agent = AnalysisAgent()
writing_agent = WritingAgent()
fact_checking_agent = FactCheckingAgent()

# Initialize LLM for revision agent
revision_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model=settings.GROQ_MODEL,
    temperature=0.6
)


# =============================================================================
# NODE DEFINITIONS
# =============================================================================

def node_research(state: ContentResearchState) -> ContentResearchState:
    """Research Node - Gather information about the topic"""
    return research_agent.execute(state)


def node_analysis(state: ContentResearchState) -> ContentResearchState:
    """Analysis Node - Analyze and organize research data"""
    return analysis_agent.execute(state)


def node_writing(state: ContentResearchState) -> ContentResearchState:
    """Writing Node - Generate initial content draft"""
    return writing_agent.execute(state)


def node_fact_checking(state: ContentResearchState) -> ContentResearchState:
    """Fact-Checking Node - Verify content accuracy"""
    return fact_checking_agent.execute(state)


def node_revision(state: ContentResearchState) -> ContentResearchState:
    """Revision Node - Revise content based on fact-check feedback"""
    print(f"\n🔄 REVISION AGENT: Revising content based on fact-check feedback")
    
    try:
        from langchain_core.prompts import PromptTemplate
        
        fact_check_analysis = state['fact_check_results'].get('analysis', '')
        original_draft = state['draft']
        
        prompt = PromptTemplate(
            input_variables=["draft", "feedback"],
            template="""Review the following fact-check feedback and revise the content accordingly.
Maintain the original structure and tone, but address the issues raised.

Original Content:
{draft}

Fact-Check Feedback:
{feedback}

Please provide the revised content:"""
        )
        
        chain = prompt | revision_llm
        result = chain.invoke({
            "draft": original_draft,
            "feedback": fact_check_analysis
        })
        
        state['draft'] = result.content
        state['draft_status'] = 'revised'
        
        print(f"✓ Content revised successfully")
        
        return state
    
    except Exception as e:
        state['error_message'] = str(e)
        print(f"✗ Revision error: {e}")
        return state


def node_finalization(state: ContentResearchState) -> ContentResearchState:
    """Finalization Node - Prepare final output with metadata"""
    print(f"\n🎯 FINALIZATION: Preparing final output")
    
    try:
        # Set final content
        state['final_content'] = state.get('draft', '')
        
        if not state['final_content']:
            print("⚠️ No content to finalize")
            state['final_content'] = "Error: No content was generated"
        
        # Prepare citations
        citations = []
        if state.get('research_data'):
            for idx, source in enumerate(state['research_data'], 1):
                if source.get('url'):
                    citations.append({
                        'number': idx,
                        'source': source.get('source', 'Unknown'),
                        'url': source.get('url')
                    })
        
        state['citations'] = citations
        
        # Prepare metadata - SAFE DEFAULTS
        word_count = len(state['final_content'].split()) if state.get('final_content') else 0
        sources_used = len(citations)
        
        # Get confidence score safely
        fact_check_results = state.get('fact_check_results', {})
        if fact_check_results is None:
            fact_check_results = {}
        
        confidence_score = fact_check_results.get('confidence_score', 75)
        if confidence_score is None:
            confidence_score = 75
        
        # Ensure confidence_score is an integer
        try:
            confidence_score = int(confidence_score)
        except (ValueError, TypeError):
            confidence_score = 75
        
        state['metadata'] = {
            'word_count': word_count,
            'content_type': state.get('content_type', 'unknown'),
            'sources_used': sources_used,
            'topic': state.get('topic', 'unknown'),
            'tone': 'professional' if state.get('content_type') == 'article' else 'engaging',
            'confidence_score': confidence_score,
            'revision_made': state.get('draft_status') == 'revised'
        }
        
        print(f"✓ Final content prepared ({word_count} words, {sources_used} sources, {confidence_score}% confidence)")
        
        return state
    
    except Exception as e:
        state['error_message'] = str(e)
        print(f"✗ Finalization error: {e}")
        
        # Return state with safe defaults
        state['final_content'] = state.get('draft', 'Error generating content')
        state['citations'] = []
        state['metadata'] = {
            'word_count': len(state.get('draft', '').split()) if state.get('draft') else 0,
            'content_type': state.get('content_type', 'unknown'),
            'sources_used': 0,
            'topic': state.get('topic', 'unknown'),
            'tone': 'unknown',
            'confidence_score': 60,
            'revision_made': False
        }
        
        return state


# =============================================================================
# CONDITIONAL ROUTING FUNCTIONS
# =============================================================================

def should_revise(state: ContentResearchState) -> str:
    """
    Conditional router after fact-checking.
    Decide whether to revise or finalize content.
    """
    if state.get('revision_needed', False):
        return "revision"
    else:
        return "finalization"


def check_research_status(state: ContentResearchState) -> str:
    """
    Conditional router after research.
    Check if research was successful before proceeding.
    """
    if state.get('research_status') == 'failed':
        return "error"
    else:
        return "analysis"


def check_analysis_status(state: ContentResearchState) -> str:
    """
    Conditional router after analysis.
    Check if analysis was successful before proceeding.
    """
    if state.get('analysis_status') == 'failed':
        return "error"
    else:
        return "writing"


def check_writing_status(state: ContentResearchState) -> str:
    """
    Conditional router after writing.
    Check if writing was successful before proceeding.
    """
    if state.get('draft_status') == 'failed':
        return "error"
    else:
        return "fact_checking"


# =============================================================================
# ERROR HANDLING NODE
# =============================================================================

def node_error_handler(state: ContentResearchState) -> ContentResearchState:
    """Error Handler Node - Handle workflow errors"""
    print(f"\n❌ ERROR: {state.get('error_message', 'Unknown error occurred')}")
    return state


# =============================================================================
# BUILD THE WORKFLOW GRAPH
# =============================================================================

def build_workflow_graph():
    """Build and return the complete LangGraph workflow"""
    
    # Create state graph
    workflow = StateGraph(ContentResearchState)
    
    # Add nodes
    workflow.add_node("research", node_research)
    workflow.add_node("analysis", node_analysis)
    workflow.add_node("writing", node_writing)
    workflow.add_node("fact_checking", node_fact_checking)
    workflow.add_node("revision", node_revision)
    workflow.add_node("finalization", node_finalization)
    workflow.add_node("error", node_error_handler)
    
    # Add edges with conditional routing
    workflow.set_entry_point("research")
    
    # Research → Analysis or Error
    workflow.add_conditional_edges(
        "research",
        check_research_status,
        {
            "analysis": "analysis",
            "error": "error"
        }
    )
    
    # Analysis → Writing or Error
    workflow.add_conditional_edges(
        "analysis",
        check_analysis_status,
        {
            "writing": "writing",
            "error": "error"
        }
    )
    
    # Writing → Fact-Checking or Error
    workflow.add_conditional_edges(
        "writing",
        check_writing_status,
        {
            "fact_checking": "fact_checking",
            "error": "error"
        }
    )
    
    # Fact-Checking → Revision or Finalization
    workflow.add_conditional_edges(
        "fact_checking",
        should_revise,
        {
            "revision": "revision",
            "finalization": "finalization"
        }
    )
    
    # Revision → Finalization
    workflow.add_edge("revision", "finalization")
    
    # Finalization → End
    workflow.add_edge("finalization", END)
    
    # Error → End
    workflow.add_edge("error", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


# =============================================================================
# WORKFLOW VISUALIZATION
# =============================================================================

def visualize_workflow():
    """Visualize the workflow graph"""
    app = build_workflow_graph()
    
    # Print graph structure
    print("\n" + "=" * 70)
    print("WORKFLOW GRAPH STRUCTURE")
    print("=" * 70)
    print(app.get_graph().draw_ascii())
    print("=" * 70)


# =============================================================================
# MAIN EXECUTION FUNCTION
# =============================================================================

def run_workflow(topic: str, content_type: str = "blog", target_audience: str = None):
    """
    Execute the complete workflow
    
    Args:
        topic: Topic to research and write about
        content_type: Type of content ("blog", "article", "social")
        target_audience: Target audience for the content
        
    Returns:
        Final state with completed content
    """
    
    # Initialize state
    initial_state = ContentResearchState(
        topic=topic,
        content_type=content_type,
        target_audience=target_audience or "General audience",
        research_data=None,
        research_status="pending",
        analysis=None,
        analysis_status="pending",
        draft=None,
        draft_status="pending",
        fact_check_results=None,
        fact_check_status="pending",
        revision_needed=False,
        final_content=None,
        citations=None,
        metadata=None,
        error_message=None
    )
    
    print("\n" + "=" * 70)
    print(f"STARTING CONTENT GENERATION WORKFLOW")
    print(f"Topic: {topic}")
    print(f"Content Type: {content_type}")
    print(f"Target Audience: {target_audience or 'General audience'}")
    print("=" * 70)
    
    # Build and run workflow
    app = build_workflow_graph()
    
    try:
        # Execute workflow
        final_state = app.invoke(initial_state)
        
        # Print results
        print_results(final_state)
        
        return final_state
    
    except Exception as e:
        print(f"\n❌ WORKFLOW ERROR: {e}")
        return initial_state


# =============================================================================
# RESULTS PRINTING
# =============================================================================

def print_results(state: ContentResearchState):
    """Print formatted final results"""
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE - FINAL RESULTS")
    print("=" * 70)
    
    # Check if workflow completed successfully
    if state.get('final_content'):
        print("\n📄 FINAL CONTENT:")
        print("-" * 70)
        print(state['final_content'])
        print("-" * 70)
        
        # Print metadata
        if state.get('metadata'):
            print("\n📊 METADATA:")
            metadata = state['metadata']
            print(f"  • Word Count: {metadata.get('word_count')} words")
            print(f"  • Content Type: {metadata.get('content_type')}")
            print(f"  • Sources Used: {metadata.get('sources_used')}")
            print(f"  • Confidence Score: {metadata.get('confidence_score')}%")
            print(f"  • Revision Made: {metadata.get('revision_made')}")
        
        # Print citations
        if state.get('citations'):
            print("\n📚 CITATIONS:")
            for citation in state['citations']:
                print(f"  [{citation['number']}] {citation['source']}")
                print(f"      URL: {citation['url']}")
    
    else:
        print("\n❌ WORKFLOW FAILED")
        if state.get('error_message'):
            print(f"Error: {state['error_message']}")
    
    print("\n" + "=" * 70)

