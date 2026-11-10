from fastapi import APIRouter, HTTPException
from app.core.datastore import CSVDataStore

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/{user_id}")
def get_user_subscription(user_id: str):
    """Fetch subscription details for a user from internal CSV store."""
    df = CSVDataStore.get_subs_df()
    match = df[df["user_id"] == user_id]
    if match.empty:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    return {"source": "internal_csv", "record": match.iloc[0].to_dict()}
