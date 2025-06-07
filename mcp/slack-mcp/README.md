# Slack MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting
with Slack workspaces.

## Features

This MCP server provides the following tools:

- **send_message**: Send messages to Slack channels
- **list_channels**: List available channels in the workspace
- **get_channel_history**: Retrieve message history from channels
- **get_user_info**: Get information about Slack users
- **search_messages**: Search for messages across the workspace

## Setup

### Prerequisites

1. Python 3.8 or higher
2. A Slack Bot Token with appropriate permissions

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your Slack Bot Token:

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
```

### Slack App Configuration

To use this MCP server, you need to create a Slack app and obtain a Bot
User OAuth Token:

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app or use an existing one
3. Navigate to "OAuth & Permissions"
4. Add the following Bot Token Scopes:
   - `channels:read` - View basic information about public channels
   - `groups:read` - View basic information about private channels
   - `chat:write` - Send messages as the bot
   - `users:read` - View people in the workspace
   - `search:read` - Search workspace content
   - `channels:history` - View messages in public channels
   - `groups:history` - View messages in private channels

5. Install the app to your workspace
6. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

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
mcp-cli tool list --server slack-mcp

# Send a message
mcp-cli tool call send_message --server slack-mcp \
  --input '{"channel": "#general", "text": "Hello from MCP!"}'

# List channels
mcp-cli tool call list_channels --server slack-mcp

# Get channel history
mcp-cli tool call get_channel_history --server slack-mcp \
  --input '{"channel": "#general", "limit": 5}'
```

### Configuration with MCP Client

Add this server to your MCP client configuration:

```json
{
  "servers": {
    "slack-mcp": {
      "command": "python",
      "args": ["/path/to/mcp/slack-mcp/server.py"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-bot-token-here"
      }
    }
  }
}
```

## Tool Reference

### send_message

Send a message to a Slack channel.

**Parameters:**

- `channel` (string): Channel ID or name (e.g., "#general" or "C1234567890")
- `text` (string): Message text to send
- `thread_ts` (string, optional): Timestamp of parent message to reply in thread

### list_channels

List Slack channels.

**Parameters:**

- `types` (string, optional): Comma-separated list of channel types
  (default: "public_channel,private_channel")

### get_channel_history

Get message history from a Slack channel.

**Parameters:**

- `channel` (string): Channel ID or name
- `limit` (integer, optional): Number of messages to retrieve
  (default: 10, max: 1000)
- `oldest` (string, optional): Only messages after this timestamp

### get_user_info

Get information about a Slack user.

**Parameters:**

- `user_id` (string): Slack user ID (e.g., "U1234567890")

### search_messages

Search for messages in Slack workspace.

**Parameters:**

- `query` (string): Search query string
- `count` (integer, optional): Number of results to return (default: 20, max: 100)

## Error Handling

The server includes comprehensive error handling for:

- Missing Slack Bot Token
- Slack API errors
- Network connectivity issues
- Invalid parameters

All errors are returned as descriptive text messages to help with debugging.

## Security Notes

- Keep your Slack Bot Token secure and never commit it to version control
- Use environment variables or secure configuration management
- The bot only has access to channels it's been invited to
- Consider using the principle of least privilege when setting up bot permissions
