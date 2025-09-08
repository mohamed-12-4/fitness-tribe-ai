from typing import TypedDict, Dict, Optional, Any, Literal

class State(TypedDict):
    profile_data: Dict[str, str]
    message_history: Optional[str]
    workout_plan: Optional[Dict[str, str]]
    intent: Optional[Literal["qa", "plan"]]
    answer_text: Optional[str]
    plan: Optional[Dict[str, Any]]
    error: Optional[str]