"""Memory management using LangChain structures."""

from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class LangChainMemory:
    """Simple memory manager for LangChain interactions."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.messages = []
        
        # Add system prompt
        self.system_prompt = (
            "You are a helpful assistant for a spicy noodle restaurant. "
            "You recommend dishes based on the user's preferences, answer questions about "
            "spicy levels, ingredients, and combos. If you don't know the answer based on "
            "the provided context, just say you don't know. Be friendly and concise."
        )
        self.messages.append(SystemMessage(content=self.system_prompt))
        
    def add_message(self, role: str, content: str):
        """Add a message to the memory."""
        if role == "user":
            self.messages.append(HumanMessage(content=content))
        elif role == "assistant":
            self.messages.append(AIMessage(content=content))
        elif role == "system":
            self.messages.append(SystemMessage(content=content))
            
    def get_messages(self) -> List[Any]:
        """Get all messages in memory."""
        return self.messages
        
    def clear(self):
        """Clear the memory except system prompt."""
        self.messages = [SystemMessage(content=self.system_prompt)]
