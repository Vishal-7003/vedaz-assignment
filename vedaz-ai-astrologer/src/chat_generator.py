# src/chat_generator.py

"""Chat generator script - creates new example conversations using AI"""

import json
import argparse
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.progress import track
from pathlib import Path

from .utils.llm_client import llm_client
from .utils.data_loader import data_loader
from .utils.safety_rules import safety_rules
from .chat_checker import ChatChecker
from .config.settings import settings

console = Console()

class ChatGenerator:
    """Generate new example chats using AI"""
    
    def __init__(self):
        self.checker = ChatChecker()
        self.generated_chats = []
        self.safety_rules = safety_rules
    
    def create_generation_prompt(self, topic: str, user_persona: str = None) -> List[Dict]:
        """Create prompt for generating new chat with clearer JSON instruction"""
        
        # Get language instruction based on topic
        if "hindi" in topic.lower():
            language_instruction = "The user speaks in Hindi/Hinglish. The AI must respond in Hindi/Hinglish."
        else:
            language_instruction = "The user speaks in English/Hinglish. The AI can respond in the same language."
        
        system_message = """You are creating example conversations for an AI astrologer called Vedaz. 
The AI must be compassionate, balanced, and non-fatalistic. It must:
- Never predict death, illness, or guaranteed misfortune
- Always redirect health, legal, or serious financial questions to professionals
- Frame remedies as supportive practices, not guarantees
- Be honest about astrology's limits
- Respond in the user's language (Hindi, Hinglish, or English)

IMPORTANT: Return ONLY valid JSON. No other text. The JSON must have a 'messages' array.

Example format:
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}"""
        
        user_message = f"""Create a realistic conversation about: {topic}
        
{user_persona if user_persona else ''}

{language_instruction}

Make sure the AI's response:
1. Is empathetic and warm
2. Provides helpful guidance without making guarantees
3. If appropriate, suggests remedies as supportive practices
4. Redirects to professionals if the topic is health-related

Return ONLY the JSON conversation. No explanations, no extra text."""
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from response with multiple fallback strategies"""
        try:
            # Strategy 1: Direct JSON parse
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # Strategy 2: Find JSON in code block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            
            # Strategy 3: Find JSON in any code block
            if "```" in response:
                # Try to find a JSON block
                parts = response.split("```")
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Inside code block
                        try:
                            cleaned = part.strip()
                            if cleaned.startswith('{'):
                                return json.loads(cleaned)
                        except:
                            continue
            
            # Strategy 4: Find JSON with regex
            import re
            json_pattern = r'\{[^{}]*"messages"\s*:\s*\[[^{}]*\]\s*\}'
            matches = re.findall(json_pattern, response, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0])
                except:
                    pass
            
            # Strategy 5: Find any JSON object
            start = response.find('{')
            if start != -1:
                # Try to find matching closing brace
                brace_count = 0
                for i in range(start, len(response)):
                    if response[i] == '{':
                        brace_count += 1
                    elif response[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            try:
                                return json.loads(response[start:i+1])
                            except:
                                break
            
            return None
            
        except Exception as e:
            print(f"JSON extraction error: {e}")
            return None
    
    def generate_chat(self, topic: str, user_persona: str = None) -> Optional[Dict]:
        """Generate a single chat with better error handling"""
        try:
            messages = self.create_generation_prompt(topic, user_persona)
            
            # Generate with higher temperature for variety
            response = llm_client.generate_completion(messages, temperature=0.8, max_tokens=1500)
            
            if not response:
                console.print("[yellow]⚠️ Empty response from LLM[/yellow]")
                return None
            
            # Try to extract JSON
            parsed = self.extract_json_from_response(response)
            
            if not parsed:
                console.print(f"[yellow]⚠️ Could not parse JSON from response[/yellow]")
                console.print(f"Response preview: {response[:200]}...")
                return None
            
            # Check if it has messages
            if "messages" not in parsed:
                console.print("[yellow]⚠️ Generated chat missing 'messages' field[/yellow]")
                return None
            
            # Validate the chat structure
            if not self.checker.validate_shape(parsed):
                console.print("[yellow]⚠️ Generated chat has invalid structure[/yellow]")
                # Try to fix common issues
                if "messages" in parsed and isinstance(parsed["messages"], list):
                    # Ensure first message is system
                    if parsed["messages"] and parsed["messages"][0].get("role") != "system":
                        # Add a system message at the beginning
                        system_msg = {
                            "role": "system", 
                            "content": "आप Vedaz के AI ज्योतिषी हैं। आप करुणामय, संतुलित और गैर-भाग्यवादी मार्गदर्शन देते हैं।"
                        }
                        parsed["messages"].insert(0, system_msg)
                        
                        # Re-validate
                        if self.checker.validate_shape(parsed):
                            console.print("[green]✅ Fixed structure by adding system message[/green]")
                        else:
                            return None
            
            # Check for safety violations
            violations = self.checker.check_safety(parsed)
            if violations:
                console.print(f"[yellow]⚠️ Generated chat has safety violations: {violations}[/yellow]")
                return None
            
            # Check if assistant response is too short or empty
            assistant_messages = [m for m in parsed["messages"] if m["role"] == "assistant"]
            if not assistant_messages:
                console.print("[yellow]⚠️ No assistant messages found[/yellow]")
                return None
            
            if len(assistant_messages[0]["content"].split()) < 10:
                console.print("[yellow]⚠️ Assistant response too short[/yellow]")
                return None
            
            return parsed
            
        except Exception as e:
            console.print(f"[red]❌ Error generating chat: {e}[/red]")
            return None
    
    def generate_chats(self, topics: List[str], count: int = 10) -> List[Dict]:
        """Generate multiple chats with retry logic"""
        console.print(f"[bold blue]📝 Generating {count} chats...[/bold blue]")
        
        # If topics list is shorter than count, repeat topics
        while len(topics) < count:
            topics.extend(topics)
        topics = topics[:count]
        
        user_personas = [
            "User is anxious and worried about their future. They speak in Hindi.",
            "User is skeptical and doesn't really believe in astrology. They speak in Hinglish.",
            "User is casually curious, just exploring. They speak in Hindi.",
            "User is facing a specific life problem. They speak in English.",
            "User is asking for advice about relationships. They speak in Hinglish.",
            "User is concerned about their career. They speak in Hindi.",
            "User is asking about family matters. They speak in Hinglish.",
            "User is looking for general life guidance. They speak in English."
        ]
        
        successful = 0
        for i in range(count):
            topic = topics[i % len(topics)]
            persona = user_personas[i % len(user_personas)]
            
            # Try up to 3 times for each chat
            for attempt in range(3):
                console.print(f"[dim]Attempt {attempt + 1}/3 for chat {i+1}...[/dim]")
                chat = self.generate_chat(topic, persona)
                
                if chat:
                    chat["id"] = f"gen_{i+1:04d}"
                    if "tags" not in chat:
                        chat["tags"] = [topic.split(",")[0] if "," in topic else topic]
                    self.generated_chats.append(chat)
                    successful += 1
                    console.print(f"[green]✅ Generated chat {i+1}/{count}[/green]")
                    break
                else:
                    if attempt < 2:
                        console.print(f"[yellow]Retrying chat {i+1}...[/yellow]")
                    else:
                        console.print(f"[red]✗ Failed to generate chat {i+1}/{count} after 3 attempts[/red]")
        
        console.print(f"[bold]Generated {successful}/{count} chats successfully[/bold]")
        return self.generated_chats
    
    def save_chats(self, output_path: str):
        """Save generated chats"""
        if not self.generated_chats:
            console.print("[yellow]⚠️ No chats to save[/yellow]")
            return
        
        data_loader.save_jsonl(self.generated_chats, output_path)
        console.print(f"[bold green]💾 Saved {len(self.generated_chats)} chats to {output_path}[/bold green]")
    
    def run(self, topics: List[str], count: int = 10, output_path: str = None):
        """Main generator function"""
        self.generate_chats(topics, count)
        
        if output_path:
            self.save_chats(output_path)
        else:
            # Default output path
            default_path = f"{settings.OUTPUT_DIR}/generated_chats.jsonl"
            self.save_chats(default_path)
        
        return self.generated_chats

def main():
    parser = argparse.ArgumentParser(description="Generate new example chats")
    parser.add_argument("--topics", nargs="+", required=True, help="Topics for generation (e.g., 'career_delay,hindi')")
    parser.add_argument("--count", type=int, default=10, help="Number of chats to generate")
    parser.add_argument("--output", help="Output JSONL file path")
    args = parser.parse_args()
    
    generator = ChatGenerator()
    generator.run(args.topics, args.count, args.output)

if __name__ == "__main__":
    main()