from langchain_groq import ChatGroq
from config.settings import settings
from typing import List

class SummarizerTool:
    """Tool for summarizing and analyzing text"""
    
    def __init__(self):
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.5
        )
    
    def summarize(self, text: str, max_length: int = 300) -> str:
        """Summarize a piece of text"""
        from langchain_core.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            input_variables=["text", "max_length"],
            template="""Summarize the following text in approximately {max_length} characters. 
Keep it concise and capture the main ideas:

Text: {text}

Summary:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"text": text, "max_length": max_length})
        return result.content
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """Extract key points from text"""
        from langchain_core.prompts import PromptTemplate
        
        prompt = PromptTemplate(
            input_variables=["text", "num_points"],
            template="""Extract {num_points} key points from the following text. 
Format as a numbered list:

Text: {text}

Key Points:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({"text": text, "num_points": num_points})
        
        # Parse the numbered list
        points = []
        for line in result.content.split("\n"):
            if line.strip() and (line[0].isdigit() or line.startswith("-")):
                points.append(line.strip())
        
        return points[:num_points]
