from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_openai import ChatOpenAI
from mcp.client import Client
from app.core.config import settings
from app.agents.state import AgentState
import re

llm = ChatOpenAI(
  model="nvidia/nemotron-3.5-lightning-30b-a3b",
  openai_api_key=settings.OPENAI_API_KEY,
  openai_api_base="https://integrate.api.nvidia.com/v1",
  temperature=0.001,
  top_p=1,
  max_tokens=4096,
  stream=False,
  extra_body={"reasoning_effort": "low"}
)

def clean_llm_text(text: str) -> str:
    """Remove any <think>...</think> reasoning tags and stray quotes."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip().strip("'\"")

# Step 0: Intent Router
async def intent_classifier_node(state: AgentState) -> dict:
    prompt = (
        "Classify the query into 'domain_query' (orders, gadgets, hardware, products, or subscriptions) "
        "or 'general_chat' (general knowledge, coding, casual chat).\n"
        f"Query: {state['user_query']}\nReturn ONLY 'domain_query' or 'general_chat'."
    )
    res = await llm.ainvoke(prompt)
    cleaned_res = clean_llm_text(res.content).lower()
    intent = "domain_query" if "domain_query" in cleaned_res else "general_chat"
    return {"intent": intent}

# Step 1: Query Internal Knowledge Store via MCP Tools & Resources
async def knowledge_store_mcp_node(state: AgentState) -> dict:
    extract_prompt = (
        f"Extract the single gadget name, order ID, or user ID from: '{state['user_query']}'. "
        "Return ONLY the keyword."
    )
    raw_keyword = (await llm.ainvoke(extract_prompt)).content
    keyword = clean_llm_text(raw_keyword)

    async with Client(settings.MCP_SERVER_URL) as mcp_client:
        # Read catalog summary resource for context awareness
        catalog_summary = await mcp_client.read_resource("kb://catalog/summary")

        # Select appropriate MCP Tool based on query context
        if "subscription" in state["user_query"].lower() or "plan" in state["user_query"].lower():
            tool_result = await mcp_client.call_tool("check_user_subscription", {"user_id": keyword})
        else:
            tool_result = await mcp_client.call_tool("search_knowledge_store", {"keyword": keyword})

        raw_text = str(tool_result.content[0].text) if tool_result.content else "NOT_FOUND"
        catalog_text = catalog_summary.contents[0].text if catalog_summary.contents else ""

        if raw_text != "NOT_FOUND" and "error" not in raw_text.lower():
            return {
                "kb_found": True,
                "raw_context": f"{raw_text} (Catalog Context: {catalog_text})",
                "source_used": "Internal Knowledge Store (MCP Tool & Resource)",
            }

    return {"kb_found": False, "raw_context": None}

# Rephrase Retrieved CSV Data using MCP Prompt (@mcp.prompt)
async def rephrase_kb_node(state: AgentState) -> dict:
    async with Client(settings.MCP_SERVER_URL) as mcp_client:
        prompt_msg = await mcp_client.get_prompt(
            "rephrase_kb_response_prompt",
            arguments={
                "user_query": state["user_query"],
                "raw_csv_data": state["raw_context"],
            },
        )
        formatted_prompt = prompt_msg.messages[0].content.text

    res = await llm.ainvoke(formatted_prompt)
    return {"final_answer": res.content}

# Step 2: Fallback to Wikipedia Agent + MCP Prompt for Gadget Details Outside CSV
async def wikipedia_agent_node(state: AgentState) -> dict:
    topic_prompt = f"Extract the gadget or product name to look up on Wikipedia from: '{state['user_query']}'. Return only the search term."
    raw_topic = (await llm.ainvoke(topic_prompt)).content
    topic = clean_llm_text(raw_topic)

    try:
        api_wrapper = WikipediaAPIWrapper(
                        top_k_results=3,              # Fetch top 3 matching Wikipedia pages (default is 3)
                        doc_content_chars_max=4000,   # Increase character limit (default is 4000)
                        lang="en"                     # Set Wikipedia language edition
                    )
        wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
        raw_text = wiki_tool.invoke({"query": topic})
        summary = raw_text.split("Summary: ", 1)[-1]
        wiki_summary = " ".join(re.split(r'(?<=[.!?])\s+', summary)[:3])
        # wiki_summary = wikipedia.summary(topic, sentences=3, auto_suggest=True)
        async with Client(settings.MCP_SERVER_URL) as mcp_client:
            prompt_msg = await mcp_client.get_prompt(
                "gadget_wikipedia_synthesis_prompt",
                arguments={"user_query": state["user_query"], "wiki_summary": wiki_summary},
            )
            formatted_prompt = prompt_msg.messages[0].content.text

        res = await llm.ainvoke(formatted_prompt)
        return {"final_answer": res.content, "source_used": "Wikipedia Agent + MCP Prompt"}
    except Exception:
        res = await llm.ainvoke(state["user_query"])
        return {"final_answer": res.content, "source_used": "General LLM Fallback"}

# Step 3: General LLM Response for Non-Domain Queries
async def general_llm_node(state: AgentState) -> dict:
    res = await llm.ainvoke(state["user_query"])
    return {"final_answer": res.content, "source_used": "General LLM"}
