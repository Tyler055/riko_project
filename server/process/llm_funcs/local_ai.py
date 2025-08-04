import requests
import json
import yaml
import os
from typing import Optional, List, Dict

# Load config
with open('../character_config.yaml', 'r') as f:
    char_config = yaml.safe_load(f)

class LocalAI:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_name = "llama3.2:3b"  # Lightweight model that runs well locally
        self.history_file = char_config.get('history_file', 'chat_history.json')
        self.system_prompt = char_config['presets']['default']['system_prompt']
        
        # Check if Ollama is running
        self.ollama_available = self.check_ollama()
        
        if not self.ollama_available:
            print("⚠️ Ollama not detected. Falling back to simple rule-based responses.")
    
    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def ensure_model_available(self) -> bool:
        """Make sure the model is downloaded"""
        if not self.ollama_available:
            return False
            
        try:
            # Check if model exists
            response = requests.get(f"{self.ollama_url}/api/tags")
            models = response.json().get('models', [])
            
            model_exists = any(model['name'].startswith(self.model_name) for model in models)
            
            if not model_exists:
                print(f"📥 Downloading {self.model_name} model... This may take a few minutes.")
                pull_response = requests.post(
                    f"{self.ollama_url}/api/pull",
                    json={"name": self.model_name},
                    stream=True
                )
                
                for line in pull_response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if 'status' in data:
                            print(f"   {data['status']}")
                        if data.get('status') == 'success':
                            print("✅ Model downloaded successfully!")
                            return True
            
            return True
            
        except Exception as e:
            print(f"❌ Error with model: {e}")
            return False
    
    def load_history(self) -> List[Dict]:
        """Load conversation history"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_history(self, history: List[Dict]):
        """Save conversation history"""
        try:
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save history: {e}")
    
    def get_ollama_response(self, user_input: str) -> str:
        """Get response from Ollama"""
        try:
            # Load conversation history
            history = self.load_history()
            
            # Build conversation context
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add recent history (last 10 messages)
            for msg in history[-10:]:
                messages.append(msg)
            
            # Add current user message
            messages.append({"role": "user", "content": user_input})
            
            # Make request to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['message']['content']
                
                # Update history
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": ai_response})
                self.save_history(history)
                
                return ai_response
            else:
                return "Sorry, I'm having trouble thinking right now..."
                
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return self.get_fallback_response(user_input)
    
    def get_fallback_response(self, user_input: str) -> str:
        """Simple rule-based responses when Ollama isn't available"""
        user_lower = user_input.lower()
        
        # Anime-style responses based on keywords
        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Oh, hello there! *waves* What brings you to talk to me today?"
        
        elif any(word in user_lower for word in ['how are you', 'how do you feel']):
            return "I'm doing great! Thanks for asking~ How about you?"
        
        elif any(word in user_lower for word in ['thank you', 'thanks']):
            return "Aww, you're welcome! *smiles* It's not like I did it for you or anything... baka!"
        
        elif any(word in user_lower for word in ['love', 'like you']):
            return "E-eh?! *blushes* Don't say such embarrassing things so suddenly!"
        
        elif any(word in user_lower for word in ['sad', 'upset', 'down']):
            return "Aww, don't be sad... *pats head gently* Want to talk about it?"
        
        elif any(word in user_lower for word in ['happy', 'excited', 'great']):
            return "Yay! I'm so happy to hear that! *bounces excitedly* Tell me more!"
        
        elif any(word in user_lower for word in ['bye', 'goodbye', 'see you']):
            return "Aww, leaving already? Take care! Come back soon, okay?"
        
        elif 'baka' in user_lower:
            return "Hey! Who are you calling baka?! *pouts* Hmph!"
        
        elif any(word in user_lower for word in ['cute', 'kawaii']):
            return "*blushes furiously* I-I'm not cute! Don't say such things!"
        
        elif '?' in user_input:
            return "Hmm, that's a good question! Let me think... *taps chin thoughtfully*"
        
        else:
            responses = [
                "That's interesting! Tell me more about that~",
                "Oh really? *tilts head curiously*",
                "Hmm, I see! What do you think about it?",
                "That sounds cool! I'd love to hear more!",
                "*nods thoughtfully* Go on...",
                "Ooh, that reminds me of something! But what were you saying?",
            ]
            import random
            return random.choice(responses)
    
    def get_response(self, user_input: str) -> str:
        """Main method to get AI response"""
        if self.ollama_available and self.ensure_model_available():
            return self.get_ollama_response(user_input)
        else:
            return self.get_fallback_response(user_input)

# Main function for compatibility
def llm_response(user_input: str) -> str:
    """Main function that replaces the OpenAI version"""
    local_ai = LocalAI()
    return local_ai.get_response(user_input)

if __name__ == "__main__":
    # Test the local AI
    ai = LocalAI()
    
    print("🎌 Testing Local Riko AI")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            break
        
        response = ai.get_response(user_input)
        print(f"Riko: {response}\n")