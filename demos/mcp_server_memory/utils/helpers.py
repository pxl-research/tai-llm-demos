"""
Helper utilities for the MCP Memory Server.
"""

import uuid
import datetime
from typing import Dict, Any

def create_memory_id() -> str:
    """Generate a unique ID for a memory item.
    
    Returns:
        str: A UUID string
    """
    return str(uuid.uuid4())

def timestamp() -> str:
    """Get the current timestamp.
    
    Returns:
        str: Current time in ISO format
    """
    return datetime.datetime.now().isoformat()

def format_response(success: bool, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Format a standard response dictionary.
    
    Args:
        success: Whether the operation was successful
        message: A message describing the result
        data: Optional data to include in the response
        
    Returns:
        dict: A formatted response dictionary
    """
    response = {
        "status": "success" if success else "error",
        "message": message
    }
    
    if data:
        if success:
            response.update(data)
        else:
            response["error_details"] = data
            
    return response
