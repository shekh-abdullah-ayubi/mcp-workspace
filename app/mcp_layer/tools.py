import json
from app.mcp_layer.instance import mcp
from app.core.datastore import CSVDataStore

@mcp.tool()
def search_knowledge_store(keyword: str) -> str:
    """Search the internal CSV DataFrame for a gadget name, product, or order ID."""
    result = CSVDataStore.search_catalog(keyword)
    return result if result else "NOT_FOUND"

@mcp.tool()
def check_user_subscription(user_id: str) -> str:
    """Look up subscription plan details for a given user_id in subscriptions.csv."""
    df = CSVDataStore.load_subs()
    match = df[df["user_id"] == user_id]
    if match.empty:
        return "NOT_FOUND"
    return match.iloc[0].to_json()

@mcp.tool()
def cancel_order_item(order_id: str, reason: str) -> str:
    """Cancel an existing order in orders.csv and persist the updated DataFrame."""
    df = CSVDataStore.load_orders()
    if order_id not in df["order_id"].values:
        return json.dumps({"status": "error", "message": f"Order {order_id} not found."})

    df.loc[df["order_id"] == order_id, "status"] = "cancelled"
    CSVDataStore.save_orders(df)
    return json.dumps({"status": "success", "order_id": order_id, "reason": reason})

@mcp.tool()
def update_subscription_plan(user_id: str, new_plan: str) -> str:
    """Upgrade or downgrade a user's subscription tier in subscriptions.csv."""
    df = CSVDataStore.load_subs()
    if user_id not in df["user_id"].values:
        return json.dumps({"status": "error", "message": f"User {user_id} not found."})

    df.loc[df["user_id"] == user_id, "plan"] = new_plan
    CSVDataStore.save_subs(df)
    return json.dumps({"status": "success", "user_id": user_id, "new_plan": new_plan})
