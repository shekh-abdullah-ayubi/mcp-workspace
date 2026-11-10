from typing import Literal
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes import (
    intent_classifier_node,
    knowledge_store_mcp_node,
    rephrase_kb_node,
    wikipedia_agent_node,
    general_llm_node,
)

# 1. Conditional Logic: Route based on user intent
def route_by_intent(state: AgentState) -> Literal["check_knowledge_store", "general_llm"]:
    """Decides whether to query domain knowledge or answer directly via LLM."""
    if state.get("intent") == "domain_query":
        return "check_knowledge_store"
    return "general_llm"

# 2. Conditional Logic: Route based on CSV Knowledge Store hit/miss
def route_by_kb_result(state: AgentState) -> Literal["rephrase_kb_answer", "wikipedia_fallback"]:
    """Routes to rephrasing if found in CSV, otherwise falls back to Wikipedia."""
    if state.get("kb_found") is True:
        return "rephrase_kb_answer"
    return "wikipedia_fallback"

def build_agent_graph():
    workflow = StateGraph(AgentState)

    # Register all agent nodes
    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("knowledge_store_mcp", knowledge_store_mcp_node)
    workflow.add_node("rephrase_kb", rephrase_kb_node)
    workflow.add_node("wikipedia_agent", wikipedia_agent_node)
    workflow.add_node("general_llm", general_llm_node)

    # Entry point
    workflow.set_entry_point("intent_classifier")

    # Conditional Branch 1: Domain Query vs. General Chat
    workflow.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "check_knowledge_store": "knowledge_store_mcp",
            "general_llm": "general_llm",
        },
    )

    # Conditional Branch 2: Found in CSV vs. Not Found (Wikipedia)
    workflow.add_conditional_edges(
        "knowledge_store_mcp",
        route_by_kb_result,
        {
            "rephrase_kb_answer": "rephrase_kb",
            "wikipedia_fallback": "wikipedia_agent",
        },
    )

    # Terminal edges
    workflow.add_edge("rephrase_kb", END)
    workflow.add_edge("wikipedia_agent", END)
    workflow.add_edge("general_llm", END)

    return workflow.compile()

agent_orchestrator = build_agent_graph()
