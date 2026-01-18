from tools.fact_checker import FactCheckerTool
from workflows.state import ContentResearchState

class FactCheckingAgent:
    """Agent responsible for fact-checking content"""
    
    def __init__(self):
        self.fact_checker = FactCheckerTool()
    
    def execute(self, state: ContentResearchState) -> ContentResearchState:
        """
        Fact-check the generated content
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with fact-check results
        """
        print(f"\n✅ FACT-CHECKING AGENT: Verifying content")
        
        try:
            if not state.get('draft'):
                state['fact_check_status'] = 'failed'
                state['error_message'] = 'No draft to fact-check'
                return state
            
            # Extract source URLs
            sources = []
            if state.get('research_data'):
                sources = [item['url'] for item in state['research_data'] if item.get('url')]
            
            # Perform fact-checking
            check_results = self.fact_checker.verify_claims(state['draft'], sources)
            
            state['fact_check_results'] = check_results
            state['fact_check_status'] = 'completed'
            state['revision_needed'] = check_results.get('has_issues', False)
            
            if state['revision_needed']:
                print(f"⚠️ Issues found - revision recommended")
            else:
                print(f"✓ Fact-check passed")
            
            return state
        
        except Exception as e:
            state['fact_check_status'] = 'failed'
            state['error_message'] = str(e)
            print(f"✗ Fact-checking error: {e}")
            return state
