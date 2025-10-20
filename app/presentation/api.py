from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.domain.entities import ChatRequest, ChatResponse, ConversationHistory
from app.application.use_cases import ChatUseCase
from app.infrastructure.redis_repository import RedisChatRepository
from app.infrastructure.gemini_client import GeminiClient

router = APIRouter()

# Initialize dependencies
chat_repository = RedisChatRepository()
gemini_client = GeminiClient()
chat_use_case = ChatUseCase(chat_repository, gemini_client)


@router.post("/chat/", response_model=ChatResponse)
async def chat_with_gemini(request: ChatRequest):
    """Chat with Gemini AI."""
    try:
        return await chat_use_case.process_chat_request(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}",
        )


@router.get("/chat/conversation/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    conversation = await chat_use_case.get_conversation_history(conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return conversation


@router.delete("/chat/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation."""
    success = await chat_use_case.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )
    return {"message": "Conversation deleted successfully"}


@router.post("/chat/session/start")
async def start_chat_session():
    """Start a new chat session."""
    try:
        await gemini_client.start_chat_session()
        return {"message": "Chat session started successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting chat session: {str(e)}",
        )


@router.post("/chat/session/reset")
async def reset_chat_session():
    """Reset the chat session."""
    try:
        await gemini_client.reset_chat_session()
        return {"message": "Chat session reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting chat session: {str(e)}",
        )


@router.get("/chat/session/history")
async def get_chat_history():
    """Get current chat session history."""
    try:
        history = await gemini_client.get_chat_history()
        return {"history": history}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting chat history: {str(e)}",
        )
