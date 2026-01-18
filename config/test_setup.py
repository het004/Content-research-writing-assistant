# test_setup.py
from config.settings import settings

def test_api_keys():
    """Test if all required API keys are properly loaded"""
    print("Testing API Key Configuration...")
    print("-" * 50)
    
    print(f"Groq API Key: {'✓ Set' if settings.GROQ_API_KEY else '✗ Missing'}")
    print(f"Groq Model: {settings.GROQ_MODEL}")
    print(f"Tavily API Key: {'✓ Set' if settings.TAVILY_API_KEY else '✗ Missing'}")
    print(f"Serper API Key: {'✓ Set' if settings.SERPER_API_KEY else '✗ Missing'}")
    print(f"News API Key: {'✓ Set' if settings.NEWS_API_KEY else '✗ Missing'}")
    
    print("-" * 50)
    
    # Validate
    try:
        settings.validate()
        print("✓ Setup complete! Ready for Phase 2")
        return True
    except ValueError as e:
        print(f"✗ Setup error: {e}")
        return False

if __name__ == "__main__":
    test_api_keys()