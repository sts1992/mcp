#!/usr/bin/env python3
"""
Slack MCP Server

A Model Context Protocol server that provides tools for interacting with Slack.
This server allows MCP clients to send messages, list channels, get message history,
and retrieve user information from Slack workspaces.

Required environment variables:
- SLACK_BOT_TOKEN: Slack Bot User OAuth Token (starts with xoxb-)
"""

import os
import logging
from typing import Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastMCP(
    name="slack-mcp-server",
    instructions="A Model Context Protocol server for Slack operations. Provides tools to send messages, list channels, get message history, and retrieve user information."
)

slack_token = os.getenv("SLACK_BOT_TOKEN")
if not slack_token:
    logger.warning("SLACK_BOT_TOKEN environment variable not set. Slack functionality will be limited.")
    slack_client = None
else:
    slack_client = WebClient(token=slack_token)


def ensure_slack_client():
    """Ensure Slack client is available and raise error if not."""
    if slack_client is None:
        raise ValueError("Slack client not initialized. Please set SLACK_BOT_TOKEN environment variable.")


@app.tool()
def send_message(channel: str, text: str, thread_ts: Optional[str] = None) -> str:
    """
    Send a message to a Slack channel.
    
    Args:
        channel: Channel ID or name (e.g., "#general" or "C1234567890")
        text: Message text to send
        thread_ts: Optional timestamp of parent message to reply in thread
        
    Returns:
        Success message with timestamp of sent message
    """
    ensure_slack_client()
    
    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        
        if response["ok"]:
            return f"Message sent successfully to {channel}. Timestamp: {response['ts']}"
        else:
            return f"Failed to send message: {response.get('error', 'Unknown error')}"
            
    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        return f"Error sending message: {str(e)}"


@app.tool()
def list_channels(types: str = "public_channel,private_channel") -> str:
    """
    List Slack channels.
    
    Args:
        types: Comma-separated list of channel types to include 
               (public_channel, private_channel, mpim, im)
               
    Returns:
        JSON string with channel information
    """
    ensure_slack_client()
    
    try:
        response = slack_client.conversations_list(
            types=types,
            exclude_archived=True
        )
        
        if response["ok"]:
            channels = []
            for channel in response["channels"]:
                channels.append({
                    "id": channel["id"],
                    "name": channel.get("name", ""),
                    "is_private": channel.get("is_private", False),
                    "is_member": channel.get("is_member", False),
                    "topic": channel.get("topic", {}).get("value", ""),
                    "purpose": channel.get("purpose", {}).get("value", "")
                })
            
            return f"Found {len(channels)} channels:\n" + "\n".join([
                f"- #{ch['name']} ({ch['id']}) - {'Private' if ch['is_private'] else 'Public'}"
                for ch in channels
            ])
        else:
            return f"Failed to list channels: {response.get('error', 'Unknown error')}"
            
    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        return f"Error listing channels: {str(e)}"


@app.tool()
def get_channel_history(channel: str, limit: int = 10, oldest: Optional[str] = None) -> str:
    """
    Get message history from a Slack channel.
    
    Args:
        channel: Channel ID or name
        limit: Number of messages to retrieve (max 1000)
        oldest: Only messages after this timestamp (Unix timestamp)
        
    Returns:
        Formatted message history
    """
    ensure_slack_client()
    
    try:
        kwargs = {
            "channel": channel,
            "limit": min(limit, 1000)
        }
        if oldest:
            kwargs["oldest"] = oldest
            
        response = slack_client.conversations_history(**kwargs)
        
        if response["ok"]:
            messages = response["messages"]
            if not messages:
                return f"No messages found in {channel}"
                
            formatted_messages = []
            for msg in reversed(messages):
                timestamp = datetime.fromtimestamp(float(msg["ts"])).strftime("%Y-%m-%d %H:%M:%S")
                user = msg.get("user", "Unknown")
                text = msg.get("text", "")
                
                if msg.get("subtype") == "bot_message":
                    user = msg.get("bot_id", "Bot")
                elif msg.get("subtype") == "file_share":
                    text = f"[File shared: {msg.get('files', [{}])[0].get('name', 'Unknown')}]"
                    
                formatted_messages.append(f"[{timestamp}] {user}: {text}")
                
            return f"Message history for {channel} ({len(messages)} messages):\n\n" + "\n".join(formatted_messages)
        else:
            return f"Failed to get channel history: {response.get('error', 'Unknown error')}"
            
    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        return f"Error getting channel history: {str(e)}"


@app.tool()
def get_user_info(user_id: str) -> str:
    """
    Get information about a Slack user.
    
    Args:
        user_id: Slack user ID (e.g., "U1234567890")
        
    Returns:
        User information as formatted string
    """
    ensure_slack_client()
    
    try:
        response = slack_client.users_info(user=user_id)
        
        if response["ok"]:
            user = response["user"]
            profile = user.get("profile", {})
            
            info = [
                f"User ID: {user['id']}",
                f"Name: {user.get('name', 'N/A')}",
                f"Real Name: {profile.get('real_name', 'N/A')}",
                f"Display Name: {profile.get('display_name', 'N/A')}",
                f"Email: {profile.get('email', 'N/A')}",
                f"Title: {profile.get('title', 'N/A')}",
                f"Status: {profile.get('status_text', 'N/A')}",
                f"Timezone: {user.get('tz', 'N/A')}",
                f"Is Admin: {user.get('is_admin', False)}",
                f"Is Bot: {user.get('is_bot', False)}",
                f"Is Deleted: {user.get('deleted', False)}"
            ]
            
            return "\n".join(info)
        else:
            return f"Failed to get user info: {response.get('error', 'Unknown error')}"
            
    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        return f"Error getting user info: {str(e)}"


@app.tool()
def search_messages(query: str, count: int = 20) -> str:
    """
    Search for messages in Slack workspace.
    
    Args:
        query: Search query string
        count: Number of results to return (max 100)
        
    Returns:
        Search results as formatted string
    """
    ensure_slack_client()
    
    try:
        response = slack_client.search_messages(
            query=query,
            count=min(count, 100)
        )
        
        if response["ok"]:
            matches = response["messages"]["matches"]
            if not matches:
                return f"No messages found for query: '{query}'"
                
            results = []
            for match in matches:
                channel_name = match.get("channel", {}).get("name", "Unknown")
                user = match.get("user", "Unknown")
                text = match.get("text", "")
                timestamp = datetime.fromtimestamp(float(match["ts"])).strftime("%Y-%m-%d %H:%M:%S")
                
                results.append(f"[{timestamp}] #{channel_name} - {user}: {text}")
                
            return f"Search results for '{query}' ({len(matches)} matches):\n\n" + "\n".join(results)
        else:
            return f"Failed to search messages: {response.get('error', 'Unknown error')}"
            
    except SlackApiError as e:
        return f"Slack API error: {e.response['error']}"
    except Exception as e:
        return f"Error searching messages: {str(e)}"


if __name__ == "__main__":
    app.run()
