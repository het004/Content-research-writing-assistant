from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from tools.news_api import NewsAPITool
from config.settings import settings
from typing import Optional

class TrendingContentAgent:
    """Agent for generating content based on trending news topics"""
    
    def __init__(self):
        self.news_tool = NewsAPITool()
        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.GROQ_MODEL,
            temperature=0.7
        )
    
    def get_trending_topics(self) -> list:
        """
        Get current trending topics from news
        
        Returns:
            List of trending topics
        """
        print("\n📰 TRENDING CONTENT AGENT: Fetching trending topics")
        
        try:
            topics = self.news_tool.get_trending_topics()
            
            if topics:
                print(f"✓ Found {len(topics)} trending topics")
                return topics
            else:
                print("✗ No trending topics found")
                return []
        
        except Exception as e:
            print(f"✗ Error fetching trending topics: {e}")
            return []
    
    def generate_from_trend(self, topic: str, content_type: str = "blog") -> dict:
        """
        Generate content based on a trending topic
        
        Args:
            topic: Trending topic
            content_type: Type of content (blog, article, social)
            
        Returns:
            Dictionary with topic info and generation prompt
        """
        print(f"\n📰 TRENDING CONTENT AGENT: Generating content for trending topic: {topic}")
        
        try:
            # Get recent news about the topic
            news_articles = self.news_tool.search_news(topic, max_results=10)
            
            if not news_articles:
                return {
                    "success": False,
                    "error": "No recent news found for this topic"
                }
            
            # Prepare context from news
            news_context = self._prepare_news_context(news_articles)
            
            # Generate content outline based on news
            outline = self._generate_outline(topic, news_context, content_type)
            
            return {
                "success": True,
                "topic": topic,
                "content_type": content_type,
                "recent_articles": len(news_articles),
                "news_summary": news_context,
                "outline": outline,
                "sources": [
                    {
                        "title": a["title"],
                        "url": a["url"],
                        "source": a["source"],
                        "date": a["published_at"]
                    }
                    for a in news_articles[:5]
                ]
            }
        
        except Exception as e:
            print(f"✗ Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_news_context(self, articles: list) -> str:
        """Prepare news context from articles"""
        context = "Recent News Summary:\n"
        for idx, article in enumerate(articles[:5], 1):
            context += f"\n{idx}. {article['title']}\n"
            context += f"   Source: {article['source']}\n"
            context += f"   Date: {article['published_at']}\n"
            context += f"   Summary: {article['summary']}\n"
        
        return context
    
    def _generate_outline(self, topic: str, news_context: str, 
                         content_type: str) -> str:
        """Generate content outline based on news"""
        
        prompt = PromptTemplate(
            input_variables=["topic", "news_context", "content_type"],
            template="""Based on these trending news articles about {topic}, 
create a content outline for a {content_type}.

{news_context}

Create an outline with:
1. Hook/Opening
2. 3-4 main sections based on the news
3. Key takeaways
4. Call to action

Outline:"""
        )
        
        chain = prompt | self.llm
        result = chain.invoke({
            "topic": topic,
            "news_context": news_context,
            "content_type": content_type
        })
        
        return result.content
