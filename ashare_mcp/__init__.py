"""
AShare-MCP - A股量化交易 MCP 服务器
"""
from .server import AShareMCPServer, mcp_run, __version__

__all__ = ["AShareMCPServer", "mcp_run", "__version__"]
