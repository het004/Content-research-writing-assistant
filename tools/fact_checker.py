from langchain_groq import ChatGroq
from config.settings import settings
from typing import List, Dict, Optional

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
        
        try:
            if not text or len(text.strip()) == 0:
                return {
                    "has_issues": False,
                    "analysis": "No content to fact-check",
                    "verification_status": "completed",
                    "confidence_score": 100,  # No content = no issues
                    "issues_found": [],
                    "verified_claims": []
                }
            
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

Provide your analysis in this EXACT format:
Issues Found: [list specific issues or write "None"]
Verified Claims: [list verified claims]
Corrections Needed: [list corrections or write "No corrections needed"]
Confidence Score: [number between 0-100]"""
            )
            
            chain = prompt | self.llm
            result = chain.invoke({"text": text, "sources": sources_text})
            
            response_text = result.content
            
            # Parse response more carefully
            has_issues = "Issues Found: None" not in response_text and "Issues Found:\nNone" not in response_text
            
            # Extract confidence score safely
            confidence_score = self._extract_confidence_score(response_text)
            
            return {
                "has_issues": has_issues,
                "analysis": response_text,
                "verification_status": "completed",
                "confidence_score": confidence_score,  # Always return a valid number
                "issues_found": has_issues,
                "verified_claims": not has_issues
            }
        
        except Exception as e:
            print(f"Fact-checking error: {e}")
            # Return safe defaults on error
            return {
                "has_issues": False,
                "analysis": f"Fact-checking could not be completed: {str(e)}",
                "verification_status": "error",
                "confidence_score": 70,  # Safe default confidence
                "issues_found": False,
                "verified_claims": True
            }
    
    def _extract_confidence_score(self, response_text: str) -> int:
        """
        Safely extract confidence score from response
        
        Args:
            response_text: LLM response text
            
        Returns:
            Confidence score between 0-100
        """
        try:
            # Look for "Confidence Score:" line
            lines = response_text.split("\n")
            
            for line in lines:
                if "Confidence Score:" in line:
                    # Extract number from line
                    parts = line.split("Confidence Score:")
                    if len(parts) > 1:
                        score_str = parts[1].strip()
                        # Try to extract first number
                        import re
                        numbers = re.findall(r'\d+', score_str)
                        if numbers:
                            score = int(numbers[0])
                            # Ensure it's between 0-100
                            return max(0, min(100, score))
            
            # Default score if not found
            return 75
        
        except Exception as e:
            print(f"Error extracting confidence score: {e}")
            return 75  # Safe default
