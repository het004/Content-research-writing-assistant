from config.settings import settings
from workflows.graph import run_workflow, visualize_workflow

def test_workflow():
    """Test the complete workflow"""
    
    # Validate settings
    settings.validate()
    
    # Test cases
    test_cases = [
        {
            "topic": "Machine Learning Applications in Healthcare",
            "content_type": "blog",
            "audience": "Healthcare professionals"
        },
        {
            "topic": "Latest Python Trends 2025",
            "content_type": "article",
            "audience": "Python developers"
        },
        {
            "topic": "AI Safety and Ethics",
            "content_type": "social",
            "audience": "Tech enthusiasts"
        }
    ]
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE WORKFLOW")
    print("=" * 70)
    
    # Run first test case
    test = test_cases[0]
    print(f"\nRunning test: {test['topic']}")
    print(f"Content Type: {test['content_type']}")
    print(f"Audience: {test['audience']}")
    
    result = run_workflow(
        topic=test['topic'],
        content_type=test['content_type'],
        target_audience=test['audience']
    )
    
    # Print result summary
    if result.get('final_content'):
        print("\n✓ TEST PASSED - Content generated successfully")
    else:
        print("\n✗ TEST FAILED - No content generated")
        if result.get('error_message'):
            print(f"Error: {result['error_message']}")


if __name__ == "__main__":
    test_workflow()