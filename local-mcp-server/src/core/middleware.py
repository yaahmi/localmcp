"""
ツール実行のミドルウェア
"""
from typing import Callable, Dict, Any
from functools import wraps
import time
from src.utils.logger import StructuredLogger


class ToolMiddleware:
    """ツール実行時のミドルウェア"""
    
    def __init__(self):
        self.logger = StructuredLogger("middleware")
    
    def logging_middleware(self, func: Callable):
        """ロギングミドルウェア"""
        @wraps(func)
        async def wrapper(tool_name: str, arguments: Dict[str, Any], *args, **kwargs):
            self.logger.info(
                "Tool execution started",
                tool=tool_name,
                args=str(arguments)
            )
            
            start_time = time.time()
            try:
                result = await func(tool_name, arguments, *args, **kwargs)
                execution_time = time.time() - start_time
                
                self.logger.info(
                    "Tool execution completed",
                    tool=tool_name,
                    execution_time_ms=f"{execution_time * 1000:.2f}"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                self.logger.error(
                    "Tool execution failed",
                    error=e,
                    tool=tool_name,
                    execution_time_ms=f"{execution_time * 1000:.2f}"
                )
                raise
        
        return wrapper