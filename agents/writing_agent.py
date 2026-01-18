from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from workflows.state import ContentResearchState
from config.settings import settings

class WritingAgent:
    """Agent responsible for writing content"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.7
        )
    
    def execute(self, state: ContentResearchState) -> ContentResearchState:
        """
        Generate content based on analysis
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with draft content
        """
        print(f"\n✍️ WRITING AGENT: Generating content")
        
        try:
            if not state.get('analysis'):
                state['draft_status'] = 'failed'
                state['error_message'] = 'No analysis data to write from'
                return state
            
            # Prepare writing prompt
            prompt = self._create_prompt(state)
            
            # Generate content
            result = self.llm.invoke(prompt)
            state['draft'] = result.content
            state['draft_status'] = 'completed'
            
            word_count = len(state['draft'].split())
            print(f"✓ Generated {word_count}-word draft")
            
            return state
        
        except Exception as e:
            state['draft_status'] = 'failed'
            state['error_message'] = str(e)
            print(f"✗ Writing error: {e}")
            return state
    
    def _create_prompt(self, state: ContentResearchState) -> str:
        """Create writing prompt based on state"""
        content_type = state['content_type']
        topic = state['topic']
        analysis = state['analysis']
        
        if content_type == "social":
            length = "Keep it short and engaging (280 characters max)"
        elif content_type == "article":
            length = "Write a comprehensive article (800-1200 words)"
        else:  # blog
            length = "Write an engaging blog post (600-900 words)"
        
        key_points_text = "\n".join(analysis['key_points'])
        
        prompt = f"""Write a {content_type} post about "{topic}".

{length}

Key points to cover:
{key_points_text}

Requirements:
- Engaging and easy to read
- Include relevant examples
- Professional tone
- Clear structure with headings
- Actionable insights

Content:"""
        
        return prompt