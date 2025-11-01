"""
入力値のバリデーション
"""
from typing import Any, Dict
from src.core.exceptions import ValidationError


class InputValidator:
    """入力値のバリデーター"""
    
    @staticmethod
    def validate_required_fields(
        arguments: Dict[str, Any],
        required_fields: list
    ) -> None:
        """必須フィールドのチェック"""
        for field in required_fields:
            if field not in arguments:
                raise ValidationError(
                    f"Required field '{field}' is missing",
                    field=field
                )
    
    @staticmethod
    def validate_type(
        value: Any,
        expected_type: type,
        field_name: str
    ) -> None:
        """型チェック"""
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Field '{field_name}' must be {expected_type.__name__}, "
                f"got {type(value).__name__}",
                field=field_name
            )
    
    @staticmethod
    def validate_range(
        value: float,
        min_value: float = None,
        max_value: float = None,
        field_name: str = "value"
    ) -> None:
        """数値の範囲チェック"""
        if min_value is not None and value < min_value:
            raise ValidationError(
                f"Field '{field_name}' must be >= {min_value}",
                field=field_name
            )
        if max_value is not None and value > max_value:
            raise ValidationError(
                f"Field '{field_name}' must be <= {max_value}",
                field=field_name
            )