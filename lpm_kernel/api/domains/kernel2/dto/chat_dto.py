"""
Chat-related DTO objects
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message"""
    role: str  # "system", "user", "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request"""
    message: Optional[str]  # Current user message
    system_prompt: str = ""  # System prompt
    role_id: Optional[str] = None  # Role UUID
    history: List[ChatMessage] = Field(default_factory=list)  # Message history
    messages: Optional[List[Dict[str, str]]] = None  # OpenAI compatible messages format
    enable_l0_retrieval: bool = True  # Enable L0 knowledge retrieval
    enable_l1_retrieval: bool = False  # Enable L1 knowledge retrieval
    temperature: float = 0.1  # Temperature parameter for controlling randomness
    max_tokens: int = 2000  # Maximum tokens to generate
    stream: bool = True  # Whether to stream response
