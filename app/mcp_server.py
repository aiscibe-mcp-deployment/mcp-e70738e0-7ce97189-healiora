import json
import logging
import os
from typing import Any
from mcp.server.fastmcp import FastMCP
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)


# Configuration
PROJECT_NAME = "healiora"
API_CONNECTIONS = {
    "Upload Spec Connection": {"base_url": "https://healiorabackend.rawcode.online", "auth_type": "none", "auth_config": {}},
}

# HTTP Client
client = httpx.AsyncClient(timeout=30.0)



# Tool Handlers
def _get_auth_headers(conn_name: str) -> dict:
    headers = {}
    conn = API_CONNECTIONS.get(conn_name, {})
    auth_type = conn.get("auth_type")
    auth_config = conn.get("auth_config", {})
    
    if auth_type == "api_key":
        key_name = auth_config.get("key_name", "X-API-Key")
        key_value = auth_config.get("api_key", "")
        headers[key_name] = key_value
    elif auth_type == "bearer":
        token = auth_config.get("token", "")
        headers["Authorization"] = f"Bearer {token}"
        
    return headers

async def call_api(method: str, endpoint: str, **kwargs) -> str:
    conn_name = "default"
    url = f"{API_CONNECTIONS[conn_name]['base_url']}{endpoint}"
    headers = _get_auth_headers(conn_name)
    
    try:
        if method == "GET":
            response = await client.get(url, params=kwargs, headers=headers)
        elif method == "POST":
            response = await client.post(url, json=kwargs, headers=headers)
        elif method == "PUT":
            response = await client.put(url, json=kwargs, headers=headers)
        elif method == "DELETE":
            response = await client.delete(url, params=kwargs, headers=headers)
        else:
            return json.dumps({"error": f"Unsupported method: {method}"})
            
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"API call failed: {str(e)}")
        return json.dumps({"error": str(e)})


# MCP Server Setup
# Note: Tools need to be registered manually in the generated code
# Example:
# @mcp.tool()
# async def my_tool(param: str) -> str:
#     return await call_api("GET", "/endpoint", param=param)

# Initialize FastMCP
mcp = FastMCP(PROJECT_NAME)

def main():
    """Run the MCP server."""
    # Get port from environment (Render sets PORT env var)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Bind to all interfaces for cloud deployment

    logger.info(f"Starting {PROJECT_NAME} MCP server on {host}:{port}...")

    # Use SSE transport for web deployment (Render, etc.)
    # This allows the server to run as an HTTP service
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
