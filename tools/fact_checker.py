from langchain_groq import ChatGroq
from config.settings import settings
from typing import List,Dict
class FactCheckerTool:
    """Tool for fact-checking and verification"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.3  # Lower temperature for consistency
        )
    
    def verify_claims(self, text: str, sources: List[str] = None) -> Dict:
        """
        Verify factual claims in the text
        
        Args:
            text: Content to fact-check
            sources: List of source URLs for verification
            
        Returns:
            Dictionary with issues found and corrections
        """
        from langchain_core.prompts import PromptTemplate
        
        sources_text = "\n".join(sources) if sources else "No specific sources provided"
        
        prompt = PromptTemplate(
            input_variables=["text", "sources"],
            template="""Fact-check the following text. Identify any claims that:
1. Seem questionable or unsupported
2. Could be misleading
3. Need clarification

Text to check:
{text}

Available sources:
{sources}

Provide your analysis in this format:
Issues Found: [list issues or "None"]
Corrections Needed: [list corrections or "No corrections needed"]
Confidence Score: [0-100]"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"text": text, "sources": sources_text})
        
        # Parse response
        response_text = result.content
        
        return {
            "has_issues": "Issues Found: None" not in response_text,
            "analysis": response_text,
            "verification_status": "completed"
        }
