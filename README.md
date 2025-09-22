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

### 1. Install
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
- Server URL: `http://127.0.0.1:8000`
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
HOST=127.0.0.1
PORT=8000
GOOGLE_CLOUD_PROJECT=your-project-id
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
```bash
export LOGGING_LEVEL=DEBUG
analytics-mcp
```

## Architecture

```
n8n/Claude ◄─── HTTP Streamable ───► FastAPI ◄─── FastMCP ───► Google Analytics APIs
           (JSON-RPC 2.0)           (Port 8000)    (Tools)
```

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [FastAPI](https://fastapi.tiangolo.com/) - HTTP server
- [Google Analytics APIs](https://developers.google.com/analytics) - Data source

## Links

- **Original GA MCP**: [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp)
- **MCP Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **n8n Integration**: [n8n.io](https://n8n.io)