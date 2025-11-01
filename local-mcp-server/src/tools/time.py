"""
時刻関連ツール
"""
from typing import Dict, Any
from datetime import datetime
from mcp.types import TextContent
from src.core.base import BaseTool


class GetTimeTool(BaseTool):
    """現在時刻を返すツール"""
    
    @property
    def name(self) -> str:
        return "get_time"
    
    @property
    def description(self) -> str:
        return "現在の日時を返します"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    async def before_execute(self, arguments: Dict[str, Any]) -> None:
        """実行前のログ"""
        self.logger.debug("Fetching current time")
    
    async def _execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """実行処理"""
        now = datetime.now()
        message = f"現在の日時: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"
        
        return [TextContent(type="text", text=message)]