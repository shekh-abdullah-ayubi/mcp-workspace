from fastapi import APIRouter, HTTPException
from app.core.datastore import CSVDataStore

router = APIRouter(prefix="/orders", tags=["Orders & Gadgets"])

@router.get("/search/{keyword}")
def search_orders_and_gadgets(keyword: str):
    """Search internal CSV store for matching orders or gadget items."""
    results = CSVDataStore.search_catalog(keyword)
    if not results:
        raise HTTPException(status_code=404, detail="No matching gadget or order in knowledge store.")
    return {"source": "internal_csv", "records": results}
