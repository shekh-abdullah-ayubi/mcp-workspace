from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    APP_NAME: str = "Demonstration of Multi-Agent MCP server"
    OPENAI_API_KEY: str = ""
    ORDERS_CSV: Path = ROOT_DIR / "data/orders.csv"
    SUBS_CSV: Path = ROOT_DIR / "data/subscriptions.csv"
    MCP_SERVER_URL: str = "http://localhost:8000/mcp-server/mcp"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
