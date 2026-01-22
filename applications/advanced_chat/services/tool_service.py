"""
Tool Service: Orchestrates tool calling and execution.
"""
import json
import sys
import os
from pathlib import Path
from typing import Callable, Optional, Dict, Any

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ToolService:
    """Manages tool definitions and execution."""

    def __init__(self, tool_on_execute: Optional[Callable] = None):
        """
        Initialize tool service.

        Args:
            tool_on_execute: Callback when a tool is executed
        """
        self.tools_list = []
        self.tool_registry = {}  # Name -> callable mapping
        self.tool_on_execute = tool_on_execute

    def register_tool(self, name: str, callable_func: Callable, descriptor: Dict[str, Any]):
        """
        Register a tool.

        Args:
            name: Tool name
            callable_func: Function to execute
            descriptor: Tool descriptor for LLM
        """
        self.tool_registry[name] = callable_func
        self.tools_list.append(descriptor)

    def clear_tools(self):
        """Clear all registered tools."""
        self.tools_list = []
        self.tool_registry = {}

    def get_tools_for_llm(self) -> list:
        """Get tool descriptors for LLM."""
        return self.tools_list.copy()

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool.

        Args:
            tool_name: Name of tool
            arguments: Arguments for tool

        Returns:
            Result from tool
        """
        if tool_name not in self.tool_registry:
            return {'error': f'Tool {tool_name} not found'}

        try:
            tool_func = self.tool_registry[tool_name]
            result = tool_func(**arguments)

            if self.tool_on_execute:
                self.tool_on_execute(tool_name, arguments, result)

            return result
        except Exception as e:
            return {'error': str(e)}

    def execute_tool_calls(self, tool_calls: list) -> list:
        """
        Execute multiple tool calls.

        Args:
            tool_calls: List of tool calls from LLM

        Returns:
            List of tool results
        """
        results = []
        for call in tool_calls:
            tool_name = call.function.name
            try:
                if call.function.arguments:
                    args = json.loads(call.function.arguments)
                else:
                    args = {}

                result = self.execute_tool(tool_name, args)

                results.append({
                    'id': call.id,
                    'name': tool_name,
                    'result': result,
                    'success': 'error' not in result
                })
            except Exception as e:
                results.append({
                    'id': call.id,
                    'name': tool_name,
                    'result': {'error': str(e)},
                    'success': False
                })

        return results
