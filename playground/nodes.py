 # Nodes
from langgraph import create_react_agent
from state import State as GraphState

def classify(state: GraphState) -> GraphState:
    intent = _classify_intent(state["user_input"])
    return {**state, "intent": intent}

async def qa_node(state: GraphState) -> GraphState:
    user_text = state["user_input"]
    sys = "You are a concise fitness assistant. Answer clearly in plain text. Do not include JSON."
    result = await llm_qa.ainvoke([SystemMessage(content=sys), HumanMessage(content=user_text)])
    text = getattr(result, "content", "") or str(result)
    return {**state, "answer_text": text}

async def plan_node(state: GraphState) -> GraphState:
    user_text = state["user_input"]

        # Create a ReAct agent with MCP tools; instruct strict JSON output
    agent = create_react_agent(
        llm_plan,
        tools,
        state_modifier=SystemMessage(content=(
            "You are a workout planner. Use tools when helpful to fetch exercises by target muscle."
            " Output ONLY JSON matching this schema and nothing else:\n"
            "{\n"
            '  "warmup": {"description": "string", "duration": number},\n'
            '  "cardio": {"description": "string", "duration": number},\n'
            '  "sessions_per_week": number,\n'
            '  "workout_sessions": [\n'
            "    {\"exercises\": [\n"
            '      {"name": "string", "sets": number, "reps": "string", "rest": number}\n'
            "    ]}\n"
            "  ],\n"
            '  "cooldown": {"description": "string", "duration": number}\n'
            "}\n"
            "Rules:\n"
            "- Pick exercises relevant to the user's goals, target muscles, and available equipment if mentioned.\n"
            "- Include sensible sets, reps, and rest. Keep durations in minutes.\n"
            "- No prose, no markdown, JSON only."
        ))
    )

    result = await agent.ainvoke(user_text)
        # LangGraph returns a dict-like; pull final text
    final_text = ""
    if isinstance(result, dict) and "messages" in result and result["messages"]:
        final_text = result["messages"][-1].content if hasattr(result["messages"][-1], "content") else str(result["messages"][-1])
    else:
        final_text = str(result)

        # Parse JSON and validate with Pydantic
    try:
        plan_json = json.loads(final_text)
    except Exception as e:
        return {**state, "error": f"Invalid JSON from model: {e}", "answer_text": final_text}

    try:
        plan_model = WorkoutPlan.model_validate(plan_json)
    except ValidationError as ve:
        return {**state, "error": f"Plan validation failed: {ve}", "plan": plan_json}

    return {**state, "plan": plan_model.model_dump()}

def route(state: GraphState) -> str:
    return "plan" if state.get("intent") == "plan" else "qa"
