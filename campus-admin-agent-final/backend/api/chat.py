from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any
import json
from backend.agent.core import CampusAdminAgent

router = APIRouter(prefix="/chat", tags=["chat"])
agent = CampusAdminAgent()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("")
async def chat_endpoint(request: ChatRequest):
    try:
        response = agent.handle_message(request.session_id, request.message)
        return {"response": response, "session_id": request.session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    async def event_stream():
        try:
            async for chunk in agent.async_stream_handle_message(request.session_id, request.message):
                if chunk == "__END__":
                    yield f"data: {json.dumps({'content': '', 'complete': True})}\n\n"
                else:
                    yield f"data: {json.dumps({'content': chunk, 'complete': False})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")