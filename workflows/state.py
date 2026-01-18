from typing import TypedDict, List, Optional

class ContentResearchState(TypedDict):
    """State schema for content research workflow"""
    
    # Input
    topic: str
    content_type: str  # "blog", "article", "social"
    target_audience: Optional[str]
    
    # Research Phase
    research_data: Optional[List[dict]]  # [{source, summary, url, key_points}, ...]
    research_status: str  # "pending", "completed", "failed"
    
    # Analysis Phase
    analysis: Optional[dict]  # {key_points, structure, insights, main_themes}
    analysis_status: str
    
    # Writing Phase
    draft: Optional[str]  # Initial content draft
    draft_status: str
    
    # Fact-checking Phase
    fact_check_results: Optional[dict]  # {issues, corrections, verified_claims}
    fact_check_status: str
    revision_needed: bool
    
    # Final Output
    final_content: Optional[str]
    citations: Optional[List[dict]]
    metadata: Optional[dict]  # {word_count, tone, sources_used, confidence_score}
    
    # Error tracking
    error_message: Optional[str]
