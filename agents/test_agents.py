from config.settings import settings
from agents.research_agent import ResearchAgent
from agents.analysis_agent import AnalysisAgent
from agents.writing_agent import WritingAgent
from agents.fact_checking_agent import FactCheckingAgent
from workflows.state import ContentResearchState

def test_agents():
    """Test all agents individually"""
    
    # Validate settings first
    settings.validate()
    
    # Initialize state
    state = ContentResearchState(
        topic="Artificial Intelligence in 2025",
        content_type="blog",
        target_audience="Tech enthusiasts",
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
    
    print("=" * 60)
    print("TESTING CONTENT RESEARCH & WRITING AGENTS")
    print("=" * 60)
    
    # Test Research Agent
    print("\n[1/4] Testing Research Agent...")
    research_agent = ResearchAgent()
    state = research_agent.execute(state)
    print(f"Status: {state['research_status']}")
    if state['error_message']:
        print(f"Error: {state['error_message']}")
    
    # Test Analysis Agent
    if state['research_status'] == 'completed':
        print("\n[2/4] Testing Analysis Agent...")
        analysis_agent = AnalysisAgent()
        state = analysis_agent.execute(state)
        print(f"Status: {state['analysis_status']}")
        if state['analysis']:
            print(f"Key Points: {state['analysis'].get('key_points')}")
    
    # Test Writing Agent
    if state['analysis_status'] == 'completed':
        print("\n[3/4] Testing Writing Agent...")
        writing_agent = WritingAgent()
        state = writing_agent.execute(state)
        print(f"Status: {state['draft_status']}")
        if state['draft']:
            print(f"Draft Preview: {state['draft'][:200]}...")
    
    # Test Fact-Checking Agent
    if state['draft_status'] == 'completed':
        print("\n[4/4] Testing Fact-Checking Agent...")
        fact_checking_agent = FactCheckingAgent()
        state = fact_checking_agent.execute(state)
        print(f"Status: {state['fact_check_status']}")
        print(f"Revision Needed: {state['revision_needed']}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_agents()