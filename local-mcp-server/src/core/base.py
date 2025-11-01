"""
改善された基底クラス
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from mcp.types import Tool, TextContent
from src.utils.logger import StructuredLogger
from src.utils.validators import InputValidator


class BaseTool(ABC):
    """すべてのツールの基底クラス"""
    
    def __init__(self):
        self.logger = StructuredLogger(self.__class__.__name__)
        self.validator = InputValidator()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """ツール名"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """ツールの説明"""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """入力スキーマ"""
        pass
    
    def get_definition(self) -> Tool:
        """ツール定義を返す"""
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )
    
    def validate_input(self, arguments: Dict[str, Any]) -> None:
        """
        入力値のバリデーション
        サブクラスでオーバーライド可能
        """
        required = self.input_schema.get("required", [])
        self.validator.validate_required_fields(arguments, required)
    
    async def execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """
        ツールを実行（テンプレートメソッドパターン）
        """
        # 1. バリデーション
        self.validate_input(arguments)
        
        # 2. 前処理
        await self.before_execute(arguments)
        
        # 3. 実行
        try:
            result = await self._execute(arguments)
        except Exception as e:
            self.logger.error("Tool execution failed", error=e)
            raise
        
        # 4. 後処理
        await self.after_execute(arguments, result)
        
        return result
    
    async def before_execute(self, arguments: Dict[str, Any]) -> None:
        """実行前の処理（フック）"""
        pass
    
    async def after_execute(
        self,
        arguments: Dict[str, Any],
        result: list[TextContent]
    ) -> None:
        """実行後の処理（フック）"""
        pass
    
    @abstractmethod
    async def _execute(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """実際の実行処理（サブクラスで実装）"""
        pass