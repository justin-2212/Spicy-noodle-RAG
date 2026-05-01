"""Conversation memory management."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json


class Message(BaseModel):
    """Chat message."""
    
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = None
    
    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)


class ConversationMemory:
    """In-memory conversation storage."""
    
    def __init__(self, session_id: str, max_messages: int = 20):
        """
        Initialize memory for session.
        
        Args:
            session_id: Unique session identifier
            max_messages: Maximum messages to keep
        """
        self.session_id = session_id
        self.max_messages = max_messages
        self.messages: List[Message] = []
    
    def add_message(self, role: str, content: str):
        """
        Add message to memory.
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        message = Message(role=role, content=content)
        self.messages.append(message)
        
        # Keep only recent messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_history(self, format_type: str = "text") -> str:
        """
        Get conversation history.
        
        Args:
            format_type: "text" or "json"
            
        Returns:
            Formatted history
        """
        if format_type == "text":
            return "\n".join([
                f"{msg.role.upper()}: {msg.content}"
                for msg in self.messages[-10:]  # Last 10 messages
            ])
        else:
            return json.dumps([msg.dict() for msg in self.messages])
    
    def clear(self):
        """Clear conversation history."""
        self.messages = []


class MemoryManager:
    """Manage multiple conversation sessions."""
    
    def __init__(self):
        """Initialize memory manager."""
        self.sessions: dict[str, ConversationMemory] = {}
    
    def get_or_create_session(self, session_id: str) -> ConversationMemory:
        """
        Get or create session memory.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationMemory for session
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory(session_id)
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session."""
        memory = self.get_or_create_session(session_id)
        memory.add_message(role, content)
    
    def get_history(self, session_id: str) -> str:
        """Get session history."""
        memory = self.get_or_create_session(session_id)
        return memory.get_history()


# Global memory manager
memory_manager = MemoryManager()
