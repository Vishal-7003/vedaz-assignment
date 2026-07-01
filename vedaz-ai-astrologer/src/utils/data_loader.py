"""Data loading and processing utilities"""

import json
import jsonlines
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd

class DataLoader:
    """Utility class for loading and processing data"""
    
    @staticmethod
    def load_json(file_path: str) -> List[Dict]:
        """Load JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def load_jsonl(file_path: str) -> List[Dict]:
        """Load JSONL file"""
        data = []
        with jsonlines.open(file_path, 'r') as reader:
            for obj in reader:
                data.append(obj)
        return data
    
    @staticmethod
    def save_json(data: Any, file_path: str, indent: int = 2):
        """Save data as JSON"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def save_jsonl(data: List[Dict], file_path: str):
        """Save data as JSONL"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with jsonlines.open(file_path, 'w') as writer:
            for item in data:
                writer.write(item)
    
    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough estimate of tokens (4 chars per token)"""
        return len(text) // 4

data_loader = DataLoader()