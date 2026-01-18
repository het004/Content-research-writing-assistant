from typing import List, Dict
from tools.web_search import WebSearchTool
from workflows.state import ContentResearchState

class ResearchAgent:
    """Agent responsible for researching a topic"""
    
    def __init__(self):
        self.search_tool = WebSearchTool()
    
    def execute(self, state: ContentResearchState) -> ContentResearchState:
        """
        Execute research for the given topic
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with research_data
        """
        print(f"\n🔍 RESEARCH AGENT: Researching topic '{state['topic']}'")
        
        try:
            # Enhance search query based on content type
            search_query = self._enhance_query(state['topic'], state['content_type'])
            
            # Perform web search
            results = self.search_tool.search(search_query, max_results=5)
            
            if not results:
                state['research_status'] = 'failed'
                state['error_message'] = 'No search results found'
                return state
            
            # Format research data
            state['research_data'] = results
            state['research_status'] = 'completed'
            
            print(f"✓ Found {len(results)} sources for '{state['topic']}'")
            
            return state
        
        except Exception as e:
            state['research_status'] = 'failed'
            state['error_message'] = str(e)
            print(f"✗ Research error: {e}")
            return state
    
    def _enhance_query(self, topic: str, content_type: str) -> str:
        """Enhance search query based on content type"""
        if content_type == "social":
            return f"{topic} latest trends 2024 2025"
        elif content_type == "article":
            return f"{topic} detailed analysis latest"
        else:  # blog
            return f"{topic} guide tutorial how-to"

