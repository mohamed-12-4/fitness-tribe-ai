from pydantic import BaseModel
from typing import List, Optional

class AgentResponse(BaseModel):
    text: str  # All text data not related to the generation
    data: Optional[dict]