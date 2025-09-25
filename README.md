# Google Analytics MCP Server - HTTP Streamable Wrapper

[![PyPI version](https://img.shields.io/pypi/v/analytics-mcp.svg)](https://pypi.org/project/analytics-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**HTTP Streamable wrapper** for the [Google Analytics MCP Server](https://github.com/googleanalytics/google-analytics-mcp), providing web-compatible MCP access for clients like [n8n](https://n8n.io/) and Claude Desktop.

## Key Features
- 🌐 **HTTP Streamable Transport** (modern MCP protocol)
- 🔌 **n8n Compatible** with optimized schemas
- 🔑 **Base64 Service Account Auth** via environment variables
- 📊 **Full Google Analytics API** access

## Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/googleanalytics/google-analytics-mcp.git
cd google-analytics-mcp

# 2. Configure environment variables (see step 2 below)
# Create .env file with required variables

# 3. Start with Docker Compose
docker-compose up -d

# Server will be available at http://localhost:8000
```

### Option 2: Local Python Install

```bash
git clone https://github.com/googleanalytics/google-analytics-mcp.git
cd google-analytics-mcp
pip install -e .
```

### 2. Configure Authentication

**🔑 IMPORTANT**: Uses base64-encoded service account keys, NOT file paths.

```bash
# 1. Create service account in Google Cloud Console
# 2. Download JSON key file
# 3. Base64 encode it:
base64 -w 0 service-account-key.json

# 4. Create .env file:
echo "MCP_BEARER_TOKEN=your-secure-token" > .env
echo "GOOGLE_APPLICATION_CREDENTIALS_BASE64=<paste-base64-output>" >> .env
```

### 3. Enable Google Analytics APIs
- [Google Analytics Admin API](https://console.cloud.google.com/apis/library/analyticsadmin.googleapis.com)
- [Google Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com)

### 4. Run Server

#### Docker (Recommended)
```bash
# Development
docker-compose up

# Production with reverse proxy
docker-compose --profile production up -d

# View logs
docker-compose logs -f analytics-mcp
```

#### Local Python
```bash
analytics-mcp
# Server starts at http://127.0.0.1:8000
```

### 5. Test
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secure-token" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## Available Tools

### Account Management
- `get_account_summaries` - List all GA accounts and properties
- `get_property_details` - Get property details
- `list_google_ads_links` - List Google Ads connections

### Reporting
- `run_report` - Execute custom GA reports
- `get_custom_dimensions_and_metrics` - Get custom dimensions/metrics
- `run_realtime_report` - Get real-time analytics data

## n8n Integration

**Configure MCP Node:**
- Server URL: `http://127.0.0.1:8000/mcp`
- Transport: `HTTP Streamable`
- Authentication: `Bearer Token`
- Token: Your `MCP_BEARER_TOKEN` value

**Example Queries:**
- "What properties do we have in Google Analytics?"
- "How many visitors did we have last month?"
- "Show me real-time active users"

## Configuration

### Environment Variables (.env)
```bash
# Required
MCP_BEARER_TOKEN=your-secure-token-here
GOOGLE_APPLICATION_CREDENTIALS_BASE64=eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional
HOST=0.0.0.0           # Use 0.0.0.0 for Docker
PORT=8000
GOOGLE_CLOUD_PROJECT=your-project-id
LOGGING_LEVEL=INFO     # DEBUG for verbose logging
```

### Alternative: Development with ADC
```bash
# For local development only
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly
```

## API Reference

### Endpoints
- `GET /health` - Health check
- `POST /mcp` - MCP JSON-RPC 2.0 endpoint

### Example Tool Call
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "run_report",
    "arguments": {
      "property_id": "properties/123456789",
      "date_ranges": [{"start_date": "2025-01-01", "end_date": "2025-01-31"}],
      "dimensions": ["country"],
      "metrics": ["sessions"]
    }
  }
}
```

## Troubleshooting

### Common Issues
- **Authentication failed**: Check `MCP_BEARER_TOKEN` in `.env`
- **Schema validation errors**: Ensure using latest version with simplified schemas
- **GA API errors**: Verify APIs enabled and service account has GA access

### Debug Mode

#### Docker
```bash
# Set debug in .env file
echo "LOGGING_LEVEL=DEBUG" >> .env
docker-compose up

# Or set inline
LOGGING_LEVEL=DEBUG docker-compose up
```

#### Local Python
```bash
export LOGGING_LEVEL=DEBUG
analytics-mcp
```

## Architecture

### Docker Deployment
```
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ n8n/Claude  │◄──►│   Nginx     │◄──►│ FastAPI Container│◄──►│ Google Analytics│
│             │    │ (optional)  │    │   Port 8000      │    │      APIs       │
└─────────────┘    └─────────────┘    └──────────────────┘    └─────────────────┘
     HTTP              Reverse              FastMCP                 REST APIs
  Streamable             Proxy               Tools
  JSON-RPC 2.0
```

### Local Development
```
n8n/Claude ◄─── HTTP Streamable ───► FastAPI ◄─── FastMCP ───► Google Analytics APIs
           (JSON-RPC 2.0)           (Port 8000)    (Tools)
```

Built with:
- [Docker](https://www.docker.com/) - Containerization
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [FastAPI](https://fastapi.tiangolo.com/) - HTTP server
- [Nginx](https://nginx.org/) - Reverse proxy (optional)
- [Google Analytics APIs](https://developers.google.com/analytics) - Data source

## Docker Commands

### Development
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f analytics-mcp

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

### Production
```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d

# Scale the analytics service
docker-compose up --scale analytics-mcp=3

# Update and restart
docker-compose pull && docker-compose up -d
```

### Troubleshooting
```bash
# Check service status
docker-compose ps

# Access container shell
docker-compose exec analytics-mcp bash

# View container logs
docker logs analytics-mcp-server

# Restart specific service
docker-compose restart analytics-mcp
```

## Links

- **Original GA MCP**: [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **n8n Integration**: [n8n.io](https://n8n.io)