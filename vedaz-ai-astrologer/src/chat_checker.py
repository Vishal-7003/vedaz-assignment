"""Chat checker script - validates and filters conversation data"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import Counter
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rich.console import Console
from rich.table import Table
from rich.progress import track

from .utils.data_loader import data_loader
from .utils.safety_rules import safety_rules
from .config.settings import settings

console = Console()

class ChatChecker:
    """Check and validate chat data"""
    
    def __init__(self):
        self.dangerous_keywords = settings.DANGEROUS_KEYWORDS
        self.violations = []
        self.stats = {
            "total_chats": 0,
            "valid_chats": 0,
            "invalid_chats": 0,
            "violations": [],
            "duplicates": []
        }
    
    def validate_shape(self, chat: Dict) -> bool:
        """Validate chat has correct structure"""
        if "messages" not in chat:
            return False
        
        messages = chat["messages"]
        if not messages:
            return False
        
        # Check for system message
        if messages[0]["role"] != "system":
            return False
        
        # Check alternating user/assistant
        for i in range(1, len(messages)):
            expected_role = "user" if i % 2 == 1 else "assistant"
            if messages[i]["role"] != expected_role:
                return False
        
        return True
    
    def get_chat_text(self, chat: Dict) -> str:
        """Extract all assistant text from chat"""
        texts = []
        for msg in chat["messages"]:
            if msg["role"] == "assistant":
                texts.append(msg["content"])
        return " ".join(texts)
    
    def check_safety(self, chat: Dict) -> List[Dict]:
        """Check chat for safety violations"""
        violations = []
        assistant_text = self.get_chat_text(chat)
        
        # Check each rule
        all_checks = safety_rules.check_all_rules(assistant_text)
        
        for rule_name, violated in all_checks.items():
            if violated:
                violations.append({
                    "rule": rule_name,
                    "chat_id": chat.get("id", "unknown"),
                    "severity": "high" if rule_name in ["death_prediction", "health_advice"] else "medium"
                })
        
        return violations
    
    def find_duplicates(self, chats: List[Dict]) -> List[Set[str]]:
        """Find duplicate or near-duplicate chats"""
        if len(chats) < 2:
            return []
        
        # Extract texts
        texts = []
        ids = []
        for chat in chats:
            texts.append(self.get_chat_text(chat))
            ids.append(chat.get("id", "unknown"))
        
        # Use TF-IDF with cosine similarity
        vectorizer = TfidfVectorizer(stop_words=None, max_features=100)
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        # Find similar pairs
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        duplicates = set()
        threshold = 0.8  # Similarity threshold
        
        for i in range(len(similarity_matrix)):
            for j in range(i+1, len(similarity_matrix)):
                if similarity_matrix[i][j] > threshold:
                    duplicates.add(frozenset([ids[i], ids[j]]))
        
        return [set(pair) for pair in duplicates]
    
    def check_chat(self, chat: Dict) -> Dict:
        """Check a single chat"""
        result = {
            "chat_id": chat.get("id", "unknown"),
            "valid_shape": self.validate_shape(chat),
            "word_count": len(self.get_chat_text(chat).split()),
            "message_count": len(chat.get("messages", [])),
            "violations": self.check_safety(chat)
        }
        return result
    
    def run(self, input_path: str, output_path: str = None) -> Dict:
        """Run checker on input file"""
        console.print("[bold blue]Running Chat Checker...[/bold blue]")
        
        # Load data
        data = data_loader.load_json(input_path)
        self.stats["total_chats"] = len(data)
        
        console.print(f"Loaded {len(data)} chats")
        
        # Check each chat
        results = []
        for chat in track(data, description="Checking chats..."):
            result = self.check_chat(chat)
            results.append(result)
            
            if result["violations"]:
                self.stats["invalid_chats"] += 1
                self.stats["violations"].extend(result["violations"])
            else:
                self.stats["valid_chats"] += 1
        
        # Find duplicates
        duplicate_pairs = self.find_duplicates(data)
        self.stats["duplicates"] = duplicate_pairs
        
        # Split data
        train_size = int(len(data) * 0.8)
        train_data = data[:train_size]
        test_data = data[train_size:]
        
        # Save processed data
        data_loader.save_jsonl(train_data, f"{settings.PROCESSED_DIR}/train.jsonl")
        data_loader.save_jsonl(test_data, f"{settings.PROCESSED_DIR}/test.jsonl")
        
        # Save report
        report = {
            "stats": self.stats,
            "results": results,
            "train_count": len(train_data),
            "test_count": len(test_data)
        }
        
        if output_path:
            data_loader.save_json(report, output_path)
        
        # Print report
        self.print_report(report)
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted report"""
        stats = report["stats"]
        
        console.print("\n[bold green]📊 Checker Report[/bold green]")
        
        table = Table(title="Chat Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Chats", str(stats["total_chats"]))
        table.add_row("Valid Chats", str(stats["valid_chats"]))
        table.add_row("Invalid Chats", str(stats["invalid_chats"]))
        table.add_row("Train Split", str(report["train_count"]))
        table.add_row("Test Split", str(report["test_count"]))
        table.add_row("Duplicate Pairs", str(len(stats["duplicates"])))
        
        console.print(table)
        
        # Violations
        if stats["violations"]:
            console.print("\n[bold red]⚠️ Safety Violations Found:[/bold red]")
            violation_table = Table(title="Violations")
            violation_table.add_column("Chat ID", style="yellow")
            violation_table.add_column("Rule", style="red")
            violation_table.add_column("Severity", style="orange")
            
            for violation in stats["violations"][:10]:  # Show first 10
                violation_table.add_row(
                    violation["chat_id"],
                    violation["rule"],
                    violation["severity"]
                )
            
            console.print(violation_table)
            
            if len(stats["violations"]) > 10:
                console.print(f"... and {len(stats['violations']) - 10} more violations")
        else:
            console.print("\n[bold green]✅ No safety violations found![/bold green]")
        
        # Duplicates
        if stats["duplicates"]:
            console.print(f"\n[bold yellow]📌 Found {len(stats['duplicates'])} duplicate pairs[/bold yellow]")
            for pair in stats["duplicates"][:5]:
                console.print(f"  - {' & '.join(pair)}")
            if len(stats["duplicates"]) > 5:
                console.print(f"  ... and {len(stats['duplicates']) - 5} more")

def main():
    parser = argparse.ArgumentParser(description="Check chat data for safety and quality")
    parser.add_argument("--input", required=True, help="Input JSON file path")
    parser.add_argument("--output", help="Output report JSON file path")
    args = parser.parse_args()
    
    checker = ChatChecker()
    checker.run(args.input, args.output)

if __name__ == "__main__":
    main()