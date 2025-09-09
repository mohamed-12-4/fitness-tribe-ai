from typing import Any
from fastmcp import FastMCP
import asyncio
import json
import requests
from mcp_utils import *
import uvicorn
# Initialize FastMCP server
mcp = FastMCP("Ghiraas MCP")

@mcp.tool()
def get_exercise_by_target(target: str) -> Any:
    """
    Fetch exercise data from the external API based on the target muscle group.
    """
    return get_exercises_by_target_muscle(target)

@mcp.tool()
def list_available_facts() -> Any:
    """
    List all available target muscles, equipment, and body parts from the exercise dataset.
    """
    return list_facts()

@mcp.tool()
def get_user_profile_tool(user_id: str) -> Any:
    """
    Retrieve user profile information from Firestore.
    """
    return get_user_profile(user_id)

@mcp.tool()
def get_user_recent_workouts_tool(user_id: str, limit: int = 10) -> Any:
    """
    Retrieve user's most recent completed workouts from Firestore, ordered from newest to oldest.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of workouts to retrieve (default: 10)
    """
    return get_user_recent_workouts(user_id, limit)

@mcp.tool()
def get_user_sleep_sessions_tool(user_id: str, limit: int = 10) -> Any:
    """
    Retrieve user's sleep logging data from Firestore, ordered by creation time from newest to oldest.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of sleep sessions to retrieve (default: 10)
    """
    return get_user_sleep_sessions(user_id, limit)

@mcp.tool()
def get_user_food_log_by_days_tool(user_id: str, limit_days: int = 7) -> Any:
    """
    Retrieve user's logged food data from Firestore, grouped by days using createdAt field.
    
    Args:
        user_id: The ID of the user
        limit_days: Maximum number of days to retrieve (default: 7)
    """
    return get_user_food_log_by_days(user_id, limit_days)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)