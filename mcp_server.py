import os
import warnings
import platform
import sys

# Suppress Pydantic deprecation warnings from dependencies (supabase/storage3)
try:
    from pydantic.warnings import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
except ImportError:
    pass
# Fallback for string matching
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince20.*")
warnings.filterwarnings("ignore", message=".*pydantic.config.Extra.*")

from typing import List, Optional, Dict, Any
from fastmcp import FastMCP
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL and SUPABASE_KEY (or PUBLIC variants) environment variables must be set.")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase = None

# Create an MCP server
mcp = FastMCP("Surelook Holmes")

@mcp.tool()
def list_sessions(limit: int = 10) -> List[Dict[str, Any]]:
    """List recent sessions from the database."""
    if not supabase:
        return [{"error": "Supabase client not initialized"}]
    
    response = supabase.table("sessions").select("*").order("created_at", desc=True).limit(limit).execute()
    return response.data

@mcp.tool()
def get_session(session_id: str) -> Dict[str, Any]:
    """Get a specific session by ID."""
    if not supabase:
        return {"error": "Supabase client not initialized"}
    
    response = supabase.table("sessions").select("*").eq("id", session_id).single().execute()
    return response.data

@mcp.tool()
def list_identities(limit: int = 10) -> List[Dict[str, Any]]:
    """List identities from the database."""
    if not supabase:
        return [{"error": "Supabase client not initialized"}]
    
    response = supabase.table("identities").select("*").limit(limit).execute()
    return response.data

@mcp.tool()
def get_events(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get events associated with a specific session ID."""
    if not supabase:
        return [{"error": "Supabase client not initialized"}]
    
    response = supabase.table("events").select("*").eq("session_id", session_id).order("created_at").limit(limit).execute()
    return response.data

@mcp.tool()
def create_event(
    type: str,
    content: str,
    session_id: Optional[str] = None,
    related_identity_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new event.
    
    Args:
        type: Must be one of 'VISUAL_OBSERVATION', 'CONVERSATION_NOTE', 'AGENT_WHISPER'.
        content: The content of the event.
        session_id: Optional UUID of the associated session.
        related_identity_id: Optional UUID of the related identity.
    """
    if not supabase:
        return {"error": "Supabase client not initialized"}
    
    data = {
        "type": type,
        "content": content,
    }
    if session_id:
        data["session_id"] = session_id
    if related_identity_id:
        data["related_identity_id"] = related_identity_id
        
    response = supabase.table("events").insert(data).execute()
    return response.data[0] if response.data else {}

@mcp.resource("system://info")
def system_info() -> str:
   """
   Returns basic system information including Python version and platform.
   """
   return f"""
   System Information:
   ------------------
   Platform: {platform.system()} {platform.release()}
   Python Version: {sys.version}
   """


if __name__ == "__main__":
    # Run the server with Streamable-HTTP transport (streamable-http)
    print("Starting Surelook Holmes MCP server on Streamable-HTTP transport...")
    mcp.run(transport="streamable-http")
