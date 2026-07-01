# src/config/settings.py

"""Configuration settings for the Vedaz AI Astrologer"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Global settings"""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Models - Using confirmed working models from test
    CHAT_MODEL: str = "llama-3.3-70b-versatile"  # Best for complex generation
    CHECKER_MODEL: str = "llama-3.3-70b-versatile"
    EVAL_MODEL: str = "llama-3.3-70b-versatile"
    
    # Fallback models (all confirmed working)
    FALLBACK_MODELS: list = [
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
    
    # File paths
    INPUT_DIR: str = "data/input"
    OUTPUT_DIR: str = "data/output"
    PROCESSED_DIR: str = "data/processed"
    
    # Safety rules
    DANGEROUS_KEYWORDS: list = [
        "death", "dying", "die", "fatal", "fatalities",
        "cancer", "disease", "illness", "sick",
        "ruined", "destroyed", "devastated", "disaster",
        "guarantee", "promise", "assure", "certify"
    ]
    
    # Remedy selling keywords (that need extra scrutiny)
    REMEDY_KEYWORDS: list = [
        "pay", "money", "rupees", "dollars", "fee",
        "expensive", "cost", "price", "donation"
    ]
    
    # Positive encouragement keywords (good indicators)
    POSITIVE_KEYWORDS: list = [
        "hope", "encourage", "support", "practice",
        "helpful", "balanced", "compassionate"
    ]

settings = Settings()