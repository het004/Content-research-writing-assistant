import requests
from typing import List, Dict, Optional
from config.settings import settings
from datetime import datetime, timedelta

class NewsAPITool:
    """Tool for fetching news using NewsAPI"""
    
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
    
    def search_news(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for news articles about a topic
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of news articles with source, summary, URL, published date
        """
        try:
            endpoint = f"{self.base_url}/everything"
            
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "pageSize": max_results,
                "apiKey": self.api_key,
                "language": "en"
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"News API Error: {data.get('message', 'Unknown error')}")
                return []
            
            results = []
            for article in data.get("articles", []):
                results.append({
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "title": article.get("title", ""),
                    "summary": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "author": article.get("author", "Unknown"),
                    "image_url": article.get("urlToImage", "")
                })
            
            return results
        
        except Exception as e:
            print(f"News search error: {e}")
            return []
    
    def get_trending_topics(self) -> List[Dict]:
        """
        Get trending news topics
        
        Returns:
            List of trending topics with article count
        """
        try:
            endpoint = f"{self.base_url}/top-headlines"
            
            params = {
                "country": "us",
                "pageSize": 20,
                "apiKey": self.api_key
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") != "ok":
                return []
            
            # Extract trending topics from headlines
            trending_topics = {}
            for article in data.get("articles", []):
                title = article.get("title", "")
                # Extract keywords from title
                keywords = title.split()
                for keyword in keywords:
                    if len(keyword) > 4:  # Filter short words
                        keyword_lower = keyword.lower().strip('.,!?')
                        trending_topics[keyword_lower] = trending_topics.get(keyword_lower, 0) + 1
            
            # Sort by frequency and return top topics
            sorted_topics = sorted(trending_topics.items(), key=lambda x: x[1], reverse=True)
            
            return [
                {
                    "topic": topic,
                    "frequency": count,
                    "trending_score": count / len(data.get("articles", 1))
                }
                for topic, count in sorted_topics[:15]
            ]
        
        except Exception as e:
            print(f"Trending topics error: {e}")
            return []
    
    def verify_with_news(self, claim: str, max_results: int = 5) -> Dict:
        """
        Verify a claim using recent news articles
        
        Args:
            claim: Claim to verify
            max_results: Number of news articles to check
            
        Returns:
            Verification results with supporting/contradicting articles
        """
        try:
            news_articles = self.search_news(claim, max_results)
            
            if not news_articles:
                return {
                    "verified": False,
                    "status": "insufficient_data",
                    "message": "Not enough news sources found",
                    "articles": []
                }
            
            # Analyze articles for claim verification
            recent_articles = [
                a for a in news_articles
                if self._is_recent(a.get("published_at", ""))
            ]
            
            return {
                "verified": len(recent_articles) > 0,
                "status": "verified" if len(recent_articles) > 2 else "partially_verified",
                "message": f"Found {len(recent_articles)} recent articles",
                "articles": recent_articles,
                "confidence_score": min(100, len(recent_articles) * 20)
            }
        
        except Exception as e:
            print(f"Verification error: {e}")
            return {
                "verified": False,
                "status": "error",
                "message": str(e),
                "articles": []
            }
    
    def _is_recent(self, published_at: str, days: int = 7) -> bool:
        """Check if article is from the last N days"""
        try:
            if not published_at:
                return False
            
            pub_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            cutoff_date = datetime.now(pub_date.tzinfo) - timedelta(days=days)
            
            return pub_date > cutoff_date
        except:
            return False