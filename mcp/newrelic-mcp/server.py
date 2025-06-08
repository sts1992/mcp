#!/usr/bin/env python3
"""
NewRelic MCP Server

A Model Context Protocol server that provides tools for interacting with NewRelic.
This server allows MCP clients to retrieve application monitoring data, metrics,
and performance information from NewRelic workspaces.

Required environment variables:
- NEWRELIC_API_KEY: NewRelic API Key for authentication
"""

import os
import logging
import json
from typing import Optional, List
from datetime import datetime, timedelta

import requests
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastMCP(
    name="newrelic-mcp-server",
    instructions="A Model Context Protocol server for NewRelic operations. Provides tools to retrieve application data, metrics, server information, and alert policies."
)

api_key = os.getenv("NEWRELIC_API_KEY")
if not api_key:
    logger.warning("NEWRELIC_API_KEY environment variable not set. NewRelic functionality will be limited.")

BASE_URL = "https://api.newrelic.com/v2"


def ensure_api_key():
    """Ensure API key is available and raise error if not."""
    if not api_key:
        raise ValueError("NewRelic API key not configured. Please set NEWRELIC_API_KEY environment variable.")


def make_request(endpoint: str, params: dict = None) -> dict:
    """Make authenticated request to NewRelic API."""
    ensure_api_key()
    
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"NewRelic API request failed: {str(e)}")


@app.tool()
def list_applications(filter_name: Optional[str] = None, filter_language: Optional[str] = None) -> str:
    """
    List NewRelic applications.
    
    Args:
        filter_name: Filter applications by name (partial match)
        filter_language: Filter applications by language (e.g., python, java, ruby)
        
    Returns:
        Formatted list of applications with their details
    """
    try:
        params = {}
        if filter_name:
            params["filter[name]"] = filter_name
        if filter_language:
            params["filter[language]"] = filter_language
            
        data = make_request("/applications.json", params)
        applications = data.get("applications", [])
        
        if not applications:
            return "No applications found matching the criteria."
            
        result = f"Found {len(applications)} applications:\n\n"
        for app in applications:
            health_status = app.get("health_status", "unknown")
            reporting = "✓" if app.get("reporting", False) else "✗"
            
            result += f"• **{app.get('name', 'Unknown')}** (ID: {app.get('id')})\n"
            result += f"  - Health: {health_status}\n"
            result += f"  - Reporting: {reporting}\n"
            result += f"  - Language: {app.get('language', 'N/A')}\n"
            
            if app.get("application_summary"):
                summary = app["application_summary"]
                result += f"  - Response Time: {summary.get('response_time', 'N/A')}ms\n"
                result += f"  - Throughput: {summary.get('throughput', 'N/A')} rpm\n"
                result += f"  - Error Rate: {summary.get('error_rate', 'N/A')}%\n"
            result += "\n"
            
        return result
        
    except Exception as e:
        return f"Error listing applications: {str(e)}"


@app.tool()
def get_application(app_id: int) -> str:
    """
    Get detailed information about a specific NewRelic application.
    
    Args:
        app_id: NewRelic application ID
        
    Returns:
        Detailed application information
    """
    try:
        data = make_request(f"/applications/{app_id}.json")
        app = data.get("application", {})
        
        if not app:
            return f"Application with ID {app_id} not found."
            
        result = f"**Application Details: {app.get('name', 'Unknown')}**\n\n"
        result += f"- **ID**: {app.get('id')}\n"
        result += f"- **Health Status**: {app.get('health_status', 'unknown')}\n"
        result += f"- **Reporting**: {'Yes' if app.get('reporting', False) else 'No'}\n"
        result += f"- **Language**: {app.get('language', 'N/A')}\n"
        
        if app.get("last_reported_at"):
            result += f"- **Last Reported**: {app.get('last_reported_at')}\n"
            
        if app.get("application_summary"):
            summary = app["application_summary"]
            result += f"\n**Performance Summary:**\n"
            result += f"- Response Time: {summary.get('response_time', 'N/A')}ms\n"
            result += f"- Throughput: {summary.get('throughput', 'N/A')} rpm\n"
            result += f"- Error Rate: {summary.get('error_rate', 'N/A')}%\n"
            result += f"- Apdex Score: {summary.get('apdex_score', 'N/A')}\n"
            
        if app.get("end_user_summary"):
            eu_summary = app["end_user_summary"]
            result += f"\n**End User Summary:**\n"
            result += f"- Response Time: {eu_summary.get('response_time', 'N/A')}ms\n"
            result += f"- Throughput: {eu_summary.get('throughput', 'N/A')} rpm\n"
            result += f"- Apdex Score: {eu_summary.get('apdex_score', 'N/A')}\n"
            
        if app.get("settings"):
            settings = app["settings"]
            result += f"\n**Settings:**\n"
            result += f"- App Apdex Threshold: {settings.get('app_apdex_threshold', 'N/A')}s\n"
            result += f"- End User Apdex Threshold: {settings.get('end_user_apdex_threshold', 'N/A')}s\n"
            result += f"- Enable Real User Monitoring: {'Yes' if settings.get('enable_real_user_monitoring', False) else 'No'}\n"
            
        return result
        
    except Exception as e:
        return f"Error getting application details: {str(e)}"


@app.tool()
def get_application_metrics(app_id: int, metric_names: str, from_time: Optional[str] = None, to_time: Optional[str] = None) -> str:
    """
    Get metrics for a specific NewRelic application.
    
    Args:
        app_id: NewRelic application ID
        metric_names: Comma-separated list of metric names (e.g., "HttpDispatcher,Apdex")
        from_time: Start time in ISO format (default: 30 minutes ago)
        to_time: End time in ISO format (default: now)
        
    Returns:
        Formatted metric data
    """
    try:
        params = {
            "names[]": metric_names.split(",")
        }
        
        if from_time:
            params["from"] = from_time
        else:
            params["from"] = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
            
        if to_time:
            params["to"] = to_time
        else:
            params["to"] = datetime.utcnow().isoformat()
            
        data = make_request(f"/applications/{app_id}/metrics/data.json", params)
        
        if not data.get("metric_data"):
            return f"No metric data found for application {app_id}."
            
        result = f"**Metrics for Application ID {app_id}**\n"
        result += f"Time Range: {params['from']} to {params['to']}\n\n"
        
        for metric in data["metric_data"]["metrics"]:
            result += f"**{metric.get('name', 'Unknown Metric')}**\n"
            
            for timeslice in metric.get("timeslices", []):
                from_ts = timeslice.get("from", "")
                to_ts = timeslice.get("to", "")
                values = timeslice.get("values", {})
                
                result += f"  Period: {from_ts} to {to_ts}\n"
                for key, value in values.items():
                    result += f"    {key}: {value}\n"
                result += "\n"
                
        return result
        
    except Exception as e:
        return f"Error getting application metrics: {str(e)}"


@app.tool()
def list_servers() -> str:
    """
    List NewRelic servers.
    
    Returns:
        Formatted list of servers with their details
    """
    try:
        data = make_request("/servers.json")
        servers = data.get("servers", [])
        
        if not servers:
            return "No servers found."
            
        result = f"Found {len(servers)} servers:\n\n"
        for server in servers:
            health_status = server.get("health_status", "unknown")
            reporting = "✓" if server.get("reporting", False) else "✗"
            
            result += f"• **{server.get('name', 'Unknown')}** (ID: {server.get('id')})\n"
            result += f"  - Health: {health_status}\n"
            result += f"  - Reporting: {reporting}\n"
            result += f"  - Host: {server.get('host', 'N/A')}\n"
            
            if server.get("summary"):
                summary = server["summary"]
                result += f"  - CPU: {summary.get('cpu', 'N/A')}%\n"
                result += f"  - Memory: {summary.get('memory', 'N/A')}%\n"
                result += f"  - Disk I/O: {summary.get('disk_io', 'N/A')}%\n"
            result += "\n"
            
        return result
        
    except Exception as e:
        return f"Error listing servers: {str(e)}"


@app.tool()
def get_alert_policies() -> str:
    """
    Get NewRelic alert policies.
    
    Returns:
        Formatted list of alert policies
    """
    try:
        data = make_request("/alert_policies.json")
        policies = data.get("policies", [])
        
        if not policies:
            return "No alert policies found."
            
        result = f"Found {len(policies)} alert policies:\n\n"
        for policy in policies:
            result += f"• **{policy.get('name', 'Unknown')}** (ID: {policy.get('id')})\n"
            result += f"  - Incident Preference: {policy.get('incident_preference', 'N/A')}\n"
            
            if policy.get("created_at"):
                result += f"  - Created: {policy.get('created_at')}\n"
            if policy.get("updated_at"):
                result += f"  - Updated: {policy.get('updated_at')}\n"
            result += "\n"
            
        return result
        
    except Exception as e:
        return f"Error getting alert policies: {str(e)}"


if __name__ == "__main__":
    app.run()
