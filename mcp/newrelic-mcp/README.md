# NewRelic MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting
with NewRelic monitoring and performance data.

## Features

This MCP server provides the following tools:

- **list_applications**: List NewRelic applications with filtering options
- **get_application**: Get detailed information about a specific application
- **get_application_metrics**: Retrieve metrics data for applications
- **list_servers**: List NewRelic servers and their status
- **get_alert_policies**: Get alert policies configured in NewRelic

## Setup

### Prerequisites

1. Python 3.8 or higher
2. A NewRelic API Key with appropriate permissions

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set up your NewRelic API Key:

```bash
export NEWRELIC_API_KEY="your-newrelic-api-key-here"
```

### NewRelic API Key Configuration

To use this MCP server, you need to obtain a NewRelic API key:

1. Log in to your NewRelic account
2. Go to "API keys" in your account settings
3. Create a new User API key or use an existing REST API key
4. Copy the API key value
5. Set it as the `NEWRELIC_API_KEY` environment variable

The API key should have permissions to:

- Read application data
- Read server data
- Read alert policies
- Access metrics data

## Usage

### Running the Server

```bash
python server.py
```

The server will start and listen for MCP protocol messages via stdio.

### Using with MCP CLI

You can test the server using the MCP CLI:

```bash
# List available tools
mcp-cli tool list --server newrelic-mcp

# List applications
mcp-cli tool call list_applications --server newrelic-mcp

# Get specific application details
mcp-cli tool call get_application --server newrelic-mcp \
  --input '{"app_id": 123456789}'

# Get application metrics
mcp-cli tool call get_application_metrics --server newrelic-mcp \
  --input '{"app_id": 123456789, "metric_names": "HttpDispatcher,Apdex"}'
```

### Configuration with MCP Client

Add this server to your MCP client configuration:

```json
{
  "servers": {
    "newrelic-mcp": {
      "command": "python",
      "args": ["/path/to/mcp/newrelic-mcp/server.py"],
      "env": {
        "NEWRELIC_API_KEY": "your-newrelic-api-key-here"
      }
    }
  }
}
```

## Tool Reference

### list_applications

List NewRelic applications with optional filtering.

**Parameters:**

- `filter_name` (string, optional): Filter applications by name (partial match)
- `filter_language` (string, optional): Filter by language (python, java, ruby, etc.)

### get_application

Get detailed information about a specific NewRelic application.

**Parameters:**

- `app_id` (integer): NewRelic application ID

### get_application_metrics

Retrieve metrics data for a specific application.

**Parameters:**

- `app_id` (integer): NewRelic application ID
- `metric_names` (string): Comma-separated list of metric names
- `from_time` (string, optional): Start time in ISO format (default: 30 minutes ago)
- `to_time` (string, optional): End time in ISO format (default: now)

**Common metric names:**

- `HttpDispatcher` - Web transaction response time
- `Apdex` - Application Performance Index
- `Errors/all` - Error rate
- `CPU/User Time` - CPU usage
- `Memory/Physical` - Memory usage

### list_servers

List NewRelic servers and their current status.

**Parameters:** None

### get_alert_policies

Get alert policies configured in your NewRelic account.

**Parameters:** None

## Error Handling

The server includes comprehensive error handling for:

- Missing NewRelic API Key
- NewRelic API errors and rate limits
- Network connectivity issues
- Invalid parameters
- Authentication failures

All errors are returned as descriptive text messages to help with debugging.

## Security Notes

- Keep your NewRelic API Key secure and never commit it to version control
- Use environment variables or secure configuration management
- The API key provides read access to your NewRelic monitoring data
- Consider using the principle of least privilege when creating API keys
- Monitor API key usage in your NewRelic account

## Troubleshooting

### Common Issues

1. **"NewRelic API key not configured" error**
   - Ensure `NEWRELIC_API_KEY` environment variable is set
   - Verify the API key is valid and not expired

2. **"403 Forbidden" errors**
   - Check that your API key has the required permissions
   - Verify you're using a User API key or REST API key (not Ingest keys)

3. **"Application not found" errors**
   - Verify the application ID exists in your NewRelic account
   - Check that the application is actively reporting data

4. **Empty metric data**
   - Ensure the application is actively reporting metrics
   - Check the time range specified in your request
   - Verify the metric names are correct for your application type
