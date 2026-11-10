from typing import TypedDict, Literal, Optional

class AgentState(TypedDict):
    user_query: str
    intent: Literal["domain_query", "general_chat"]
    kb_found: bool
    raw_context: Optional[str]
    source_used: str
    final_answer: str
