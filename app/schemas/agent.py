from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any

class AgentResponse(BaseModel):
    text: str  # All text data not related to the generation
    data: Optional[Union[dict, Any]] = Field(default=None, description="Response data, can be dict or null")