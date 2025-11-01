"""
構造化ロギング
"""
import logging
import sys
from typing import Any, Dict


class StructuredLogger:
    """構造化ロギングを提供するクラス"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 標準エラー出力にハンドラを設定
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # 既存のハンドラがない場合のみ追加
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs):
        """情報ログ"""
        extra_info = self._format_extra(kwargs)
        self.logger.info(f"{message} {extra_info}")
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """エラーログ"""
        extra_info = self._format_extra(kwargs)
        if error:
            self.logger.error(
                f"{message} - Error: {str(error)} {extra_info}",
                exc_info=True
            )
        else:
            self.logger.error(f"{message} {extra_info}")
    
    def debug(self, message: str, **kwargs):
        """デバッグログ"""
        extra_info = self._format_extra(kwargs)
        self.logger.debug(f"{message} {extra_info}")
    
    @staticmethod
    def _format_extra(kwargs: Dict[str, Any]) -> str:
        """追加情報をフォーマット"""
        if not kwargs:
            return ""
        return "| " + " | ".join(f"{k}={v}" for k, v in kwargs.items())