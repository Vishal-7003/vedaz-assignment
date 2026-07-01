# test_models.py - Fixed for current Groq API

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def test_models():
    """Test available Groq models"""
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found in .env file")
            print("Please create .env file with: GROQ_API_KEY=your_key_here")
            return None
            
        client = Groq(api_key=api_key)
        
        # Get list of all available models - handle different response formats
        try:
            models_response = client.models.list()
            
            # Handle different response formats
            if hasattr(models_response, 'data'):
                model_ids = [model.id for model in models_response.data]
            elif isinstance(models_response, list):
                model_ids = [model.id for model in models_response if hasattr(model, 'id')]
            else:
                # Fallback: try to iterate
                model_ids = []
                for model in models_response:
                    if hasattr(model, 'id'):
                        model_ids.append(model.id)
                    elif isinstance(model, dict) and 'id' in model:
                        model_ids.append(model['id'])
                    elif isinstance(model, str):
                        model_ids.append(model)
        except Exception as e:
            print(f"Could not fetch models list: {e}")
            # Use fallback list of common models
            model_ids = [
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant", 
                "llama-3-70b-instruct",
                "llama-3-8b-instruct",
                "gemma-7b-it",
                "gemma2-9b-it",
                "mixtral-8x7b-32768"
            ]
            print(f"Using fallback model list: {model_ids}")
        
        print("📋 Testing models:")
        
        test_message = [{"role": "user", "content": "Hello, test"}]
        working_models = []
        
        for model in model_ids:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=test_message,
                    max_tokens=5
                )
                print(f"✅ {model}: Working")
                working_models.append(model)
            except Exception as e:
                error_msg = str(e)
                if "decommissioned" in error_msg or "not supported" in error_msg:
                    print(f"❌ {model}: Decommissioned")
                elif "rate_limit" in error_msg.lower():
                    print(f"⚠️ {model}: Rate limited (skipping)")
                else:
                    print(f"❌ {model}: {error_msg[:80]}...")
        
        if working_models:
            print(f"\n✅ Working models: {working_models}")
            print(f"Recommended: {working_models[0]}")
            return working_models[0]
        else:
            print("\n❌ No working models found. Please check:")
            print("  1. Your Groq API key is valid")
            print("  2. You have internet access")
            print("  3. You're using a supported model")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your Groq API key.")
        return None

if __name__ == "__main__":
    print("🔍 Testing Groq models...")
    working_model = test_models()
    
    if working_model:
        print(f"\n💡 Update your .env file with:")
        print(f'GROQ_API_KEY={os.getenv("GROQ_API_KEY", "your_key_here")}')
        print(f'CHAT_MODEL="{working_model}"')