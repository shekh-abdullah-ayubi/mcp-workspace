import contextlib
from fastapi import FastAPI
from app.core.config import settings
from app.api.frontend import router as frontend_router

# Import MCP instance and register decorators
from app.mcp_layer.instance import mcp
import app.mcp_layer.resources
import app.mcp_layer.tools
import app.mcp_layer.prompts

# Build the MCP Streamable HTTP ASGI sub-app
mcp_http_app = mcp.streamable_http_app(streamable_http_path="/mcp")

# Start the MCP session manager inside FastAPI's lifespan
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app = FastAPI(title=settings.APP_NAME, version="2.0.0", lifespan=lifespan)

# 1. Expose REST endpoints exclusively for the Frontend
app.include_router(frontend_router)

# 2. Mount the MCP Server (accessible at http://localhost:8000/mcp-server/mcp)
app.mount("/mcp-server", mcp_http_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
