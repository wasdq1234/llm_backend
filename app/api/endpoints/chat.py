"""Chat API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.services.chat_service import ChatService
from app.services.chat_tool_service import ChatToolService
from app.api.dependencies.chat import get_chat_service
from app.models.chat import (
    ChatRequest,
    ChatResponse,
    StreamChunk,
    ErrorResponse
)
import asyncio

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a chat message and get response"""
    try:
        if request.stream:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use /chat/stream endpoint for streaming responses"
            )
        
        response_content = await chat_service.chat(
            message=request.message,
            messages=request.messages,
            conversation_id=request.conversation_id,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            message=response_content,
            conversation_id=request.conversation_id or "new",
            model=request.model or "default"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Stream chat response"""
    try:
        async def generate_stream():
            async for chunk in chat_service.stream_chat(
                message=request.message,
                messages=request.messages,
                conversation_id=request.conversation_id,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                # Format as Server-Sent Events
                chunk_data = chunk.model_dump_json()
                yield f"data: {chunk_data}\n\n"
                
                # Add small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
            
            # Send end signal
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/profile/{profile_id}/stream")
async def stream_chat_with_profile(
    profile_id: str,
    request: ChatRequest
):
    """프로필 기반 도구를 사용한 스트리밍 채팅"""
    try:
        chat_tool_service = ChatToolService()
        
        async def generate_stream():
            async for chunk in chat_tool_service.stream_chat_with_profile_tools(
                message=request.message,
                profile_id=profile_id,
                messages=request.messages,
                conversation_id=request.conversation_id,
                model=request.model
            ):
                # Format as Server-Sent Events
                chunk_data = chunk.model_dump_json()
                yield f"data: {chunk_data}\n\n"
                
                # Add small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
            
            # Send end signal
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로필 채팅 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat"} 