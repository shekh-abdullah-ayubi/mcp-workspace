import json
import pandas as pd
from app.core.config import settings

class CSVDataStore:
    @staticmethod
    def load_orders() -> pd.DataFrame:
        return pd.read_csv(settings.ORDERS_CSV, dtype={"order_id": str, "user_id": str})

    @staticmethod
    def save_orders(df: pd.DataFrame) -> None:
        df.to_csv(settings.ORDERS_CSV, index=False)

    @staticmethod
    def load_subs() -> pd.DataFrame:
        return pd.read_csv(settings.SUBS_CSV, dtype={"user_id": str})

    @staticmethod
    def save_subs(df: pd.DataFrame) -> None:
        df.to_csv(settings.SUBS_CSV, index=False)

    @staticmethod
    def search_catalog(keyword: str) -> str:
        df = CSVDataStore.load_orders()
        mask = (
            df["item"].str.contains(keyword, case=False, na=False) |
            df["order_id"].str.contains(keyword, case=False, na=False)
        )
        records = df[mask].to_dict(orient="records")
        return json.dumps(records) if records else ""
