"""
改善されたツールレジストリ
"""
from typing import Dict, List, Optional
from mcp.types import Tool, TextContent
from src.core.base import BaseTool
from src.core.exceptions import ToolNotFoundError, ToolExecutionError
from src.core.middleware import ToolMiddleware
from src.utils.logger import StructuredLogger


class ToolRegistry:
    """ツールの登録と管理"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = StructuredLogger("registry")
        self.middleware = ToolMiddleware()
    
    def register(self, tool: BaseTool) -> None:
        """ツールを登録"""
        tool_name = tool.name
        
        if tool_name in self.tools:
            self.logger.error(
                f"Tool '{tool_name}' is already registered. Overwriting."
            )
        
        self.tools[tool_name] = tool
        self.logger.info(f"Tool registered", tool=tool_name)
    
    def register_multiple(self, tools: List[BaseTool]) -> None:
        """複数のツールを一括登録"""
        for tool in tools:
            self.register(tool)
    
    def unregister(self, tool_name: str) -> None:
        """ツールの登録を解除"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(f"Tool unregistered", tool=tool_name)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """ツールを取得"""
        return self.tools.get(name)
    
    def get_all_definitions(self) -> List[Tool]:
        """すべてのツール定義を取得"""
        return [tool.get_definition() for tool in self.tools.values()]
    
    @ToolMiddleware().logging_middleware
    async def execute_tool(
        self,
        name: str,
        arguments: Dict
    ) -> List[TextContent]:
        """ツールを実行"""
        tool = self.get_tool(name)
        
        if not tool:
            raise ToolNotFoundError(name)
        
        try:
            return await tool.execute(arguments)
        except Exception as e:
            raise ToolExecutionError(name, e)
    
    def list_tool_names(self) -> List[str]:
        """登録されているツール名のリストを取得"""
        return list(self.tools.keys())
    
    def __len__(self) -> int:
        """登録されているツールの数"""
        return len(self.tools)