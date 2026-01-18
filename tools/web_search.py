import requests
from typing import List, Dict
from config.settings import settings

class WebSearchTool:
    """Web search tool using Tavily API"""
    
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.base_url = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web for information about a topic
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with source, summary, and URL
        """
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "max_results": max_results,
                "include_answer": True,
                "include_raw_content": False
            }
            
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results
            results = []
            if data.get("answer"):
                results.append({
                    "source": "Direct Answer",
                    "summary": data["answer"],
                    "url": "",
                    "key_points": [data["answer"]]
                })
            
            for result in data.get("results", []):
                results.append({
                    "source": result.get("title", "Unknown"),
                    "summary": result.get("content", ""),
                    "url": result.get("url", ""),
                    "key_points": [result.get("content", "")[:200]]
                })
            
            return results
        
        except Exception as e:
            print(f"Search error: {e}")
            return []

