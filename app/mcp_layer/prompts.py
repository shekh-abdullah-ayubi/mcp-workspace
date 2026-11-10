from app.mcp_layer.instance import mcp

@mcp.prompt()
def rephrase_kb_response_prompt(user_query: str, raw_csv_data: str) -> str:
    """Standardized enterprise prompt for rephrasing raw CSV records for customers."""
    return (
        "You are a senior customer support specialist. Rephrase the following raw database "
        "record into a clear, polite, and accurate answer tailored to the user's question.\n\n"
        f"User Question: {user_query}\n"
        f"Verified Knowledge Store Data: {raw_csv_data}\n\n"
        "Do not mention JSON, CSV, or internal database schemas."
    )

@mcp.prompt()
def gadget_wikipedia_synthesis_prompt(user_query: str, wiki_summary: str) -> str:
    """Prompt template used when an item is outside the internal CSV store."""
    return (
        "The requested gadget is not in our internal order catalog, so external product "
        "knowledge was retrieved. Answer the user's question clearly using this summary:\n\n"
        f"User Question: {user_query}\n"
        f"External Product Reference: {wiki_summary}"
    )

@mcp.prompt()
def order_escalation_audit_prompt(order_id: str) -> str:
    """Audit prompt instructing an agent to inspect order history before issuing refunds."""
    return (
        f"Review order #{order_id} using the 'kb://orders/{order_id}' resource. "
        "Verify whether the item status is 'delivered' or 'processing' before calling any cancellation tools."
    )
