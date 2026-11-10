from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.graph import agent_orchestrator

router = APIRouter(prefix="/api/v1", tags=["Frontend Gateway"])

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    source: str

@router.post("/chat", response_model=ChatResponse)
async def frontend_chat(payload: ChatRequest):
    """Endpoint exposed exclusively to the Frontend UI to trigger the Multi-Agent workflow."""
    initial_state = {
        "user_query": payload.query,
        "intent": "general_chat",
        "kb_found": False,
        "raw_context": None,
        "source_used": "",
        "final_answer": "",
    }
    result = await agent_orchestrator.ainvoke(initial_state)
    return ChatResponse(answer=result["final_answer"], source=result["source_used"])

@router.get("/health")
async def health_check():
    """Frontend health check endpoint."""
    return {"status": "healthy", "mcp_mounted": True}
