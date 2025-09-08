from app.schemas.agent import AgentResponse
from fastapi import APIRouter, HTTPException
from app.services.agent_service import agent



router = APIRouter()


@router.post("/generate", response_model=AgentResponse)
async def get_agent_response(user_message: str, user_id: str = None):
    try:
        return await agent(user_message, user_id=user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))