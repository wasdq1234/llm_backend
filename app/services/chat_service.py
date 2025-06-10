"""Chat service using LangGraph and LangChain"""

import uuid
from typing import AsyncGenerator, Optional, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import Annotated, TypedDict

from app.core.config import settings
from app.models.chat import StreamChunk, ChatMessage, MessageRole


class ChatState(TypedDict):
    """Chat state for LangGraph"""
    messages: Annotated[list, add_messages]
    conversation_id: str
    model_name: str


class ChatService:
    """Chat service using LangGraph for conversation management"""
    
    def __init__(self):
        self.memory = MemorySaver()
        self.graph = self._create_chat_graph()
        
    def _get_llm(self, model_name: str = None):
        """Get LLM instance based on model name"""
        model = model_name or settings.default_model
        
        if model.startswith("gpt"):
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ChatOpenAI(
                model=model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                openai_api_key=settings.openai_api_key,
                streaming=True
            )
        elif model.startswith("claude"):
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return ChatAnthropic(
                model=model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                anthropic_api_key=settings.anthropic_api_key,
                streaming=True
            )
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    def _create_chat_graph(self) -> StateGraph:
        """Create LangGraph for chat conversation"""
        
        async def chat_node(state: ChatState):
            """Main chat node that processes messages"""
            llm = self._get_llm(state.get("model_name"))
            
            # Add system message if not present
            messages = state["messages"]
            if not any(isinstance(msg, SystemMessage) for msg in messages):
                system_msg = SystemMessage(
                    content="당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 친절하게 답변해주세요."
                )
                messages = [system_msg] + messages
            
            # Get response from LLM
            response = await llm.ainvoke(messages)
            
            return {
                "messages": [response],
                "conversation_id": state["conversation_id"],
                "model_name": state["model_name"]
            }
        
        # Create graph
        workflow = StateGraph(ChatState)
        workflow.add_node("chat", chat_node)
        workflow.set_entry_point("chat")
        workflow.add_edge("chat", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _convert_messages_to_langchain(self, messages: List[ChatMessage]) -> List:
        """Convert ChatMessage list to LangChain message format"""
        langchain_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.USER:
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                langchain_messages.append(AIMessage(content=msg.content))
            elif msg.role == MessageRole.SYSTEM:
                langchain_messages.append(SystemMessage(content=msg.content))
        
        return langchain_messages

    async def chat(
        self,
        message: str,
        messages: Optional[List[ChatMessage]] = None,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Process chat message and return response"""
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Create thread config
        config = {"configurable": {"thread_id": conversation_id}}
        
        # Prepare messages
        if messages:
            # Use provided conversation history
            input_messages = self._convert_messages_to_langchain(messages)
        else:
            # Use single message
            input_messages = [HumanMessage(content=message)]
        
        # Prepare input
        input_data = {
            "messages": input_messages,
            "conversation_id": conversation_id,
            "model_name": model or settings.default_model
        }
        
        try:
            # Process through graph
            result = await self.graph.ainvoke(input_data, config=config)
            
            # Extract response
            last_message = result["messages"][-1]
            return last_message.content
        except Exception as e:
            # Return a simple response if LLM is not available
            return f"죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 오류: {str(e)}"
    
    async def stream_chat(
        self,
        message: str,
        messages: Optional[List[ChatMessage]] = None,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[StreamChunk, None]:
        """Stream chat response"""
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        try:
            # Create thread config
            config = {"configurable": {"thread_id": conversation_id}}
            
            # Prepare messages
            if messages:
                # Use provided conversation history
                input_messages = self._convert_messages_to_langchain(messages)
            else:
                # Use single message
                input_messages = [HumanMessage(content=message)]
            
            # Prepare input
            input_data = {
                "messages": input_messages,
                "conversation_id": conversation_id,
                "model_name": model or settings.default_model
            }
            
            # Stream through graph
            accumulated_content = ""
            async for chunk in self.graph.astream(input_data, config=config):
                if "chat" in chunk:
                    messages = chunk["chat"]["messages"]
                    if messages:
                        last_message = messages[-1]
                        if hasattr(last_message, 'content'):
                            content = last_message.content
                            if content != accumulated_content:
                                new_content = content[len(accumulated_content):]
                                accumulated_content = content
                                
                                yield StreamChunk(
                                    content=new_content,
                                    conversation_id=conversation_id,
                                    is_final=False
                                )
            
            # Send final chunk
            yield StreamChunk(
                content="",
                conversation_id=conversation_id,
                is_final=True
            )
            
        except Exception as e:
            # Yield error message as stream
            error_msg = f"죄송합니다. 현재 AI 서비스에 연결할 수 없습니다. 오류: {str(e)}"
            yield StreamChunk(
                content=error_msg,
                conversation_id=conversation_id,
                is_final=True
            ) 