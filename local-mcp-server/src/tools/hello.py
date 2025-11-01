"""
Hello ツール
"""
from typing import Dict, Any
from mcp.types import TextContent
from src.core.base import BaseTool


class HelloTool(BaseTool):
    """挨拶を返すツール"""
    
    @property
    def name(self) -> str:
        return "hello"
    
    @property
    def description(self) -> str:
        return "シンプルな挨拶を返します"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "挨拶する相手の名前"
                }
            },
            "required": ["name"]
        }
    
    def validate_input(self, arguments: Dict[str, Any]) -> None:
        """カスタムバリデーション"""
        super().validate_input(arguments)
        
        name = arguments.get("name", "")
        self.validator.validate_type(name, str, "name")
        
        if len(name) > 50:
            raise ValueError("名前は50文字以内にしてください")
    
    async def _execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """実行処理"""
        user_name = arguments["name"]
        message = f"こんにちは、{user_name}さん！🎉\nMCPサーバーから挨拶します。"
        
        return [TextContent(type="text", text=message)]