# view_chats.py - View generated chats

import json
from src.utils.data_loader import data_loader
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

def view_chats(file_path: str = "data/output/generated_chats.jsonl"):
    """View generated chats in a readable format"""
    try:
        chats = data_loader.load_jsonl(file_path)
        
        console.print(f"\n[bold green]📚 Generated Chats ({len(chats)})[/bold green]\n")
        
        for i, chat in enumerate(chats, 1):
            console.print(f"[bold cyan]{'='*50}[/bold cyan]")
            console.print(f"[bold]Chat #{i}:[/bold] {chat.get('id', 'unknown')}")
            console.print(f"[bold]Tags:[/bold] {chat.get('tags', [])}")
            console.print(f"[bold]{'-'*40}[/bold]")
            
            for msg in chat.get("messages", []):
                role = msg["role"]
                content = msg["content"]
                
                # Truncate long content for display
                if len(content) > 300:
                    content = content[:300] + "..."
                
                if role == "system":
                    console.print(f"[dim]{role}: {content}[/dim]")
                elif role == "user":
                    console.print(f"[yellow]{role}: {content}[/yellow]")
                else:
                    console.print(f"[green]{role}: {content}[/green]")
                
                console.print()
            
            console.print(f"[bold cyan]{'='*50}[/bold cyan]\n")
        
        # Summary
        console.print("[bold]Summary:[/bold]")
        console.print(f"  Total chats: {len(chats)}")
        
        # Count by language
        hindi_count = 0
        for chat in chats:
            for msg in chat.get("messages", []):
                if "hindi" in msg.get("content", "").lower():
                    hindi_count += 1
                    break
        
        console.print(f"  Chats with Hindi content: {hindi_count}")
        
    except FileNotFoundError:
        console.print("[red]❌ File not found. Generate chats first:[/red]")
        console.print("  python -m src.chat_generator --topics 'career,hindi' 'marriage,anxious' --count 6")

if __name__ == "__main__":
    view_chats()