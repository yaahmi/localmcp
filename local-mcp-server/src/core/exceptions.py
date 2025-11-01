"""
カスタム例外クラス
"""

class MCPToolError(Exception):
    """MCP ツールの基底例外クラス"""
    pass


class ToolNotFoundError(MCPToolError):
    """ツールが見つからない"""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"Tool not found: {tool_name}")


class ToolExecutionError(MCPToolError):
    """ツール実行エラー"""
    def __init__(self, tool_name: str, original_error: Exception):
        self.tool_name = tool_name
        self.original_error = original_error
        super().__init__(
            f"Error executing tool '{tool_name}': {str(original_error)}"
        )


class ValidationError(MCPToolError):
    """バリデーションエラー"""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)