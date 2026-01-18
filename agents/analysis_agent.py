from langchain_groq import ChatGroq
from tools.summarizer import SummarizerTool
from workflows.state import ContentResearchState
from config.settings import settings
from typing import List,Dict
class AnalysisAgent:
    """Agent responsible for analyzing research data"""
    
    def __init__(self):
        self.summarizer = SummarizerTool()
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.6
        )
    
    def execute(self, state: ContentResearchState) -> ContentResearchState:
        """
        Analyze and organize research findings
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with analysis
        """
        print(f"\n📊 ANALYSIS AGENT: Analyzing research data")
        
        try:
            if not state.get('research_data'):
                state['analysis_status'] = 'failed'
                state['error_message'] = 'No research data to analyze'
                return state
            
            # Combine all research data
            combined_text = self._combine_research_data(state['research_data'])
            
            # Extract key points
            key_points = self.summarizer.extract_key_points(combined_text, num_points=5)
            
            # Generate structure
            structure = self._generate_structure(state['topic'], key_points)
            
            # Create analysis
            state['analysis'] = {
                'key_points': key_points,
                'structure': structure,
                'combined_insights': combined_text[:500],
                'main_themes': self._extract_themes(key_points)
            }
            
            state['analysis_status'] = 'completed'
            print(f"✓ Analysis complete with {len(key_points)} key points")
            
            return state
        
        except Exception as e:
            state['analysis_status'] = 'failed'
            state['error_message'] = str(e)
            print(f"✗ Analysis error: {e}")
            return state
    
    def _combine_research_data(self, research_data: List[Dict]) -> str:
        """Combine all research data into a single text"""
        combined = []
        for item in research_data:
            combined.append(f"Source: {item['source']}\n{item['summary']}")
        return "\n\n".join(combined)
    
    def _generate_structure(self, topic: str, key_points: List[str]) -> Dict:
        """Generate article structure based on key points"""
        return {
            'introduction': f"Overview of {topic}",
            'main_sections': key_points,
            'conclusion': f"Summary and insights about {topic}"
        }
    
    def _extract_themes(self, key_points: List[str]) -> List[str]:
        """Extract main themes from key points"""
        # Simple implementation - can be enhanced with NLP
        themes = set()
        for point in key_points:
            words = point.lower().split()
            themes.update([w for w in words if len(w) > 5])
        return list(themes)[:3]
