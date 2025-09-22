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

"""HTTP Streamable server for the Google Analytics MCP using FastMCP's native transport."""

import os
import logging
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


def run_http_streamable_server() -> None:
    """Runs the HTTP Streamable server using FastMCP's native transport.
    
    This uses FastMCP's built-in streamable HTTP transport,
    which is the modern standard for MCP communication.
    
    Configuration is handled via environment variables:
    - HOST: Server host (default: 127.0.0.1)
    - PORT: Server port (default: 8000)
    """
    # Set default environment variables if not set
    if "HOST" not in os.environ:
        os.environ["HOST"] = "127.0.0.1"
    if "PORT" not in os.environ:
        os.environ["PORT"] = "8000"
    
    host = os.environ.get("HOST")
    port = os.environ.get("PORT")
    
    logger.info(f"Starting Google Analytics MCP server with HTTP Streamable transport")
    logger.info(f"Server will be available at http://{host}:{port}")
    
    # Use FastMCP's run method with streamable HTTP transport
    # Host and port are configured via environment variables
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    run_http_streamable_server()
