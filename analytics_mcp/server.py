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
from fastapi.security import OAuth2PasswordBearer
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

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

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_token(token: str = Depends(oauth2_scheme)):
    correct_token = os.environ.get("MCP_BEARER_TOKEN")
    logger.info(f"Correct token: {correct_token}")
    logger.info(f"Received token: {token}")
    if not correct_token or token != correct_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@app.post("/mcp")
@app.post("/mcp/")
async def mcp_endpoint(request: Request, token: str = Depends(get_current_token)):
    """SSE endpoint for the MCP server."""
    try:
        body = await request.json()
        logger.info(f"Received request: {body}")

        async def event_generator():
            # This is where we would call the mcp.process method
            # Since mcp.process is not directly available, we need to simulate it
            # by calling the tools directly based on the 'prompt' in the body.
            # This is a placeholder for the actual logic to parse the prompt
            # and call the appropriate tool.
            # For now, we'll just return a dummy response.
            yield json.dumps({"response": "MCP server is running and authenticated."})

        return EventSourceResponse(event_generator())
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e}",
        )


def run_server() -> None:
    """Runs the server.

    Serves as the entrypoint for the 'analytics-mcp' command.
    """
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_server()
