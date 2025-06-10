"""Chat-related data models"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message model"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., min_length=1, max_length=10000)
    messages: Optional[List[ChatMessage]] = Field(default=None, description="Conversation history including current message")
    conversation_id: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=4000)
    stream: bool = Field(default=True)


class ChatResponse(BaseModel):
    """Chat response model"""
    message: str
    conversation_id: str
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class StreamChunk(BaseModel):
    """Streaming response chunk"""
    content: str
    conversation_id: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None


class ConversationSummary(BaseModel):
    """Conversation summary model"""
    conversation_id: str
    title: Optional[str] = None
    message_count: int
    created_at: datetime
    last_updated: datetime
    preview: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now) 