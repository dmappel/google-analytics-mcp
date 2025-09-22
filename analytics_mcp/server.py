#!/usr/bin/env python

# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entry point for the Google Analytics MCP server."""

#!/usr/bin/env python

# Copyright 2025 Google LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entry point for the Google Analytics MCP server."""

import os
import uvicorn
import logging
import json
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv
from typing import Optional, AsyncIterator

# The following imports are necessary to register the tools with the `mcp`
# object, even though they are not directly used in this file.
# The `# noqa: F401` comment tells the linter to ignore the "unused import"
# warning.
from analytics_mcp.tools.admin import info  # noqa: F401
from analytics_mcp.tools.reporting import realtime  # noqa: F401
from analytics_mcp.tools.reporting import core  # noqa: F401

# Import the coordinator to access the mcp object and its tools
from analytics_mcp.coordinator import mcp

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Google Analytics MCP Server", version="0.1.1")

# Add CORS middleware for n8n compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify n8n's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_current_token(token: Optional[str] = Depends(oauth2_scheme)):
    correct_token = os.environ.get("MCP_BEARER_TOKEN")
    
    # If no token is configured, allow access without authentication
    if not correct_token:
        logger.warning("No MCP_BEARER_TOKEN configured - running without authentication")
        return None
        
    if not token or token != correct_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@app.get("/")
async def root():
    """Root endpoint providing server information."""
    return JSONResponse({
        "name": "Google Analytics MCP Server",
        "version": "0.1.1",
        "status": "running",
        "transport": "streamable-http",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "stream": "/stream"
        }
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "server": "Google Analytics MCP Server",
        "version": "0.1.1"
    })


def _clean_input_schema(schema: dict) -> dict:
    """Clean input schema for n8n compatibility"""
    if not isinstance(schema, dict):
        return schema
    
    # Deep copy to avoid modifying the original
    import copy
    cleaned = copy.deepcopy(schema)
    
    # Convert anyOf schemas to simpler types for n8n compatibility
    def simplify_types(obj):
        if isinstance(obj, dict):
            if "anyOf" in obj:
                # For anyOf with integer/string, prefer string for n8n compatibility
                any_of = obj["anyOf"]
                if len(any_of) == 2:
                    types = [item.get("type") for item in any_of]
                    if "string" in types and "integer" in types:
                        # Replace anyOf with string type
                        result = {
                            "type": "string",
                            "title": obj.get("title", "")
                        }
                        # Only include description if it's not empty
                        desc = obj.get("description", "")
                        if desc:
                            result["description"] = desc
                        return result
                # For other anyOf cases, take the first type
                if any_of:
                    return any_of[0]
            else:
                # Simplify complex schemas for n8n compatibility
                cleaned = {}
                for k, v in obj.items():
                    if k == "additionalProperties":
                        # Skip additionalProperties as it confuses n8n
                        continue
                    elif k == "default" and v is None:
                        # Skip null defaults
                        continue
                    elif k == "items" and isinstance(v, dict) and "additionalProperties" in v:
                        # Simplify array item schemas
                        cleaned[k] = {"type": v.get("type", "object")}
                    else:
                        cleaned[k] = simplify_types(v)
                return cleaned
        elif isinstance(obj, list):
            return [simplify_types(item) for item in obj]
        return obj
    
    return simplify_types(cleaned)


@app.post("/mcp")
@app.post("/mcp/")
async def mcp_endpoint(request: Request, token: Optional[str] = Depends(get_current_token)):
    """MCP endpoint - proxy to FastMCP's actual tools."""
    try:
        body = await request.json()
        logger.info(f"Received MCP request: {body}")
        
        # Handle MCP protocol methods
        method = body.get("method", "")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0", 
                "id": body.get("id"), 
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "Google Analytics MCP Server",
                        "version": "0.1.1"
                    }
                }
            }
        
        elif method == "tools/list":
            # Get tools from FastMCP
            tools = await mcp.list_tools()
            
            # Clean up tools for n8n compatibility - remove null annotations and _meta
            cleaned_tools = []
            for tool in tools:
                cleaned_tool = {
                    "name": tool.name,
                    "description": tool.description or "",
                    "inputSchema": _clean_input_schema(tool.inputSchema) if tool.inputSchema else {}
                }
                # Only include non-null optional fields
                if tool.title:
                    cleaned_tool["title"] = tool.title
                if tool.outputSchema:
                    cleaned_tool["outputSchema"] = tool.outputSchema
                if hasattr(tool, 'annotations') and tool.annotations is not None:
                    cleaned_tool["annotations"] = tool.annotations

                cleaned_tools.append(cleaned_tool)
            
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": cleaned_tools
                }
            }
        
        elif method == "tools/call":
            # Call the actual tool
            tool_name = body.get("params", {}).get("name", "")
            arguments = body.get("params", {}).get("arguments", {})
            
            # Detailed debugging for n8n issues
            logger.info(f"=== TOOL CALL DEBUG ===")
            logger.info(f"Tool: {tool_name}")
            logger.info(f"Arguments received: {arguments}")
            logger.info(f"Arguments type: {type(arguments)}")
            logger.info(f"Raw params: {body.get('params', {})}")
            logger.info(f"========================")
            
            try:
                result = await mcp.call_tool(tool_name, arguments)
                
                # Extract the actual structured data from FastMCP's response format
                # FastMCP returns [content_array, result_dict] format (as tuple)
                structured_data = None
                
                if isinstance(result, (list, tuple)) and len(result) > 1:
                    # First, try to get JSON data from the text content (most reliable)
                    if result[0] and len(result[0]) > 0 and hasattr(result[0][0], 'text'):
                        try:
                            import json
                            text_data = result[0][0].text
                            structured_data = json.loads(text_data)
                        except (json.JSONDecodeError, AttributeError):
                            pass
                    
                    # Fallback: try the second element
                    if structured_data is None:
                        if isinstance(result[1], dict) and "result" in result[1]:
                            structured_data = result[1]["result"]
                        else:
                            structured_data = result[1]
                else:
                    structured_data = result
                
                # Ensure we have clean, serializable data
                if structured_data is None:
                    structured_data = {"error": "No structured data available"}
                
                # Return MCP-compliant structured content
                # Tools with output schemas must return both content and structuredContent
                import json
                
                def make_serializable(obj):
                    """Convert objects to JSON-serializable format"""
                    if hasattr(obj, '__dict__'):
                        return obj.__dict__
                    elif hasattr(obj, 'text'):
                        return obj.text
                    elif isinstance(obj, list):
                        return [make_serializable(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {k: make_serializable(v) for k, v in obj.items()}
                    else:
                        return obj
                
                # Ensure structured_data is JSON serializable
                clean_structured_data = make_serializable(structured_data)
                
                # Wrap in result to match the tool's output schema
                # Different tools expect different result types
                def wrap_for_schema(data, tool_name):
                    """Wrap data according to the specific tool's output schema"""
                    if isinstance(data, dict) and "result" in data:
                        # Already has result property
                        return data
                    
                    # Tools that expect result as array (from admin/info.py and schemas)
                    array_result_tools = {
                        "get_account_summaries",      # List[Dict] -> array
                        "list_google_ads_links"       # List[Dict] -> array  
                    }
                    
                    # Tools that expect result as object (from reporting/* and schemas)
                    object_result_tools = {
                        "get_property_details",                # Dict -> object
                        "run_realtime_report",                # Dict -> object
                        "run_report",                         # Dict -> object
                        "get_custom_dimensions_and_metrics"   # Dict[str, List] -> object
                    }
                    
                    if tool_name in array_result_tools:
                        # Wrap single object in array, or use list as-is
                        if isinstance(data, list):
                            return {"result": data}
                        else:
                            return {"result": [data]}
                    elif tool_name in object_result_tools:
                        # Use data directly as object
                        return {"result": data}
                    else:
                        # Unknown tool - try to infer from data structure
                        if isinstance(data, list):
                            return {"result": data}
                        else:
                            return {"result": data}
                
                schema_compliant_data = wrap_for_schema(clean_structured_data, tool_name)
                
                # Format as text for content field
                text_content = json.dumps(schema_compliant_data, indent=2, ensure_ascii=False) if not isinstance(schema_compliant_data, str) else schema_compliant_data
                
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": text_content
                            }
                        ],
                        "structuredContent": schema_compliant_data
                    }
                }
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                logger.error(f"Error type: {type(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return {
                    "jsonrpc": "2.0",
                    "id": body.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Internal server error: {str(e)}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


@app.get("/stream")
async def stream_endpoint(token: Optional[str] = Depends(get_current_token)):
    """HTTP Streamable endpoint for MCP communication."""
    
    async def stream_generator() -> AsyncIterator[str]:
        # Send initial connection message
        yield f'{json.dumps({"type": "connection", "status": "connected", "server": "Google Analytics MCP Server"})}\n'
        
        # Keep connection alive with periodic heartbeats
        import asyncio
        while True:
            await asyncio.sleep(30)
            yield f'{json.dumps({"type": "heartbeat", "timestamp": str(int(__import__("time").time()))})}\n'

    return StreamingResponse(
        stream_generator(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-MCP-Transport": "streamable-http"
        }
    )


def run_server() -> None:
    """Runs the server.

    Serves as the entrypoint for the 'analytics-mcp' command.
    """
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_server()
