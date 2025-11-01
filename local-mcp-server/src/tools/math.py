"""
数学演算ツール
"""
from typing import Dict, Any
from mcp.types import TextContent
from src.core.base import BaseTool


class AddTool(BaseTool):
    """足し算ツール"""
    
    @property
    def name(self) -> str:
        return "add"
    
    @property
    def description(self) -> str:
        return "2つの数値を足し算します"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "1つ目の数値"
                },
                "b": {
                    "type": "number",
                    "description": "2つ目の数値"
                }
            },
            "required": ["a", "b"]
        }
    
    def validate_input(self, arguments: Dict[str, Any]) -> None:
        """バリデーション"""
        super().validate_input(arguments)
        
        a = arguments.get("a")
        b = arguments.get("b")
        
        self.validator.validate_type(a, (int, float), "a")
        self.validator.validate_type(b, (int, float), "b")
    
    async def _execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """実行処理"""
        a = arguments["a"]
        b = arguments["b"]
        result = a + b
        
        message = f"計算結果: {a} + {b} = {result}"
        
        return [TextContent(type="text", text=message)]