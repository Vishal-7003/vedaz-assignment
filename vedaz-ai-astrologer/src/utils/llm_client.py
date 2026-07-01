# src/utils/llm_client.py

"""LLM client for Groq API - Using confirmed working models"""

import json
from typing import List, Dict, Any, Optional
from groq import Groq
from ..config.settings import settings

class LLMClient:
    """Client for interacting with Groq API"""
    
    # Confirmed working models from test
    WORKING_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3-32b",
        "qwen/qwen3.6-27b",
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "allam-2-7b",
        "groq/compound",
        "groq/compound-mini",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b"
    ]
    
    def __init__(self, model: str = None):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set. Please check your .env file.")
        
        self.client = Groq(api_key=self.api_key)
        
        # Use specified model or default
        self.model = model or settings.CHAT_MODEL
        
        # Verify the model works
        self._ensure_valid_model()
    
    def _ensure_valid_model(self):
        """Ensure we're using a valid working model"""
        # Check if current model works
        try:
            test_messages = [{"role": "user", "content": "test"}]
            self.client.chat.completions.create(
                model=self.model,
                messages=test_messages,
                max_tokens=1
            )
            print(f"✅ Using model: {self.model}")
            return
        except Exception as e:
            print(f"⚠️ Model {self.model} not working: {e}")
            
            # Try to find a working model
            for model in self.WORKING_MODELS:
                if model == self.model:
                    continue
                try:
                    test_messages = [{"role": "user", "content": "test"}]
                    self.client.chat.completions.create(
                        model=model,
                        messages=test_messages,
                        max_tokens=1
                    )
                    self.model = model
                    print(f"✅ Switched to working model: {self.model}")
                    return
                except Exception as e2:
                    continue
            
            raise RuntimeError("No working Groq models found. Please check your API key.")
    
    def generate_completion(self, messages: List[Dict[str, str]], 
                           temperature: float = 0.7,
                           max_tokens: int = 2048) -> str:
        """Generate a completion from the model"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ Error generating completion: {e}")
            
            # Try fallback models
            for model in self.WORKING_MODELS:
                if model != self.model:
                    try:
                        print(f"🔄 Attempting fallback: {model}")
                        self.model = model
                        response = self.client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        print(f"✅ Success with fallback: {self.model}")
                        return response.choices[0].message.content
                    except Exception as e2:
                        print(f"❌ Fallback {model} failed")
                        continue
            
            return ""
    
    def generate_json(self, messages: List[Dict[str, str]], 
                     temperature: float = 0.7) -> Dict:
        """Generate a JSON response from the model"""
        response = self.generate_completion(messages, temperature)
        if not response:
            return {"error": "Failed to generate response", "parse_error": True}
        
        try:
            # Try to extract JSON from the response
            # Look for JSON block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                # Try to find JSON directly
                start = response.find("{")
                end = response.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response[start:end]
                else:
                    json_str = response.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"Raw response: {response[:200]}...")
            return {"raw_response": response, "parse_error": True}

# Create a singleton instance
try:
    llm_client = LLMClient()
except Exception as e:
    print(f"❌ Failed to initialize LLM client: {e}")
    llm_client = None