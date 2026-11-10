import json
from app.mcp_layer.instance import mcp
from app.core.datastore import CSVDataStore

@mcp.resource("kb://orders/all", mime_type="application/json")
def get_all_orders_resource() -> str:
    """Read the complete orders and gadget catalog DataFrame."""
    df = CSVDataStore.load_orders()
    return df.to_json(orient="records")

@mcp.resource("kb://orders/{order_id}", mime_type="application/json")
def get_order_by_id_resource(order_id: str) -> str:
    """Fetch a single order record by order_id from the CSV DataFrame."""
    df = CSVDataStore.load_orders()
    match = df[df["order_id"] == order_id]
    if match.empty:
        return json.dumps({"error": f"Order {order_id} not found"})
    return match.iloc[0].to_json()

@mcp.resource("kb://subscriptions/{user_id}", mime_type="application/json")
def get_subscription_by_user_resource(user_id: str) -> str:
    """Fetch active subscription tier and billing amount for a user."""
    df = CSVDataStore.load_subs()
    match = df[df["user_id"] == user_id]
    if match.empty:
        return json.dumps({"error": f"Subscription for {user_id} not found"})
    return match.iloc[0].to_json()

@mcp.resource("kb://catalog/summary", mime_type="text/plain")
def get_catalog_metrics_resource() -> str:
    """Return high-level summary statistics of the CSV knowledge store."""
    df = CSVDataStore.load_orders()
    return f"Total Orders: {len(df)} | Unique Gadgets: {df['item'].nunique()} | Active Items: {', '.join(df['item'].unique())}"
