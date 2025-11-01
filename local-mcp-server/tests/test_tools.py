"""
ツールのユニットテスト
"""
import pytest
from src.tools.hello import HelloTool
from src.tools.math import AddTool
from src.tools.time import GetTimeTool
from src.core.exceptions import ValidationError


@pytest.mark.asyncio
async def test_hello_tool():
    """HelloToolのテスト"""
    tool = HelloTool()
    
    # 正常系
    result = await tool.execute({"name": "太郎"})
    assert len(result) == 1
    assert "太郎" in result[0].text
    
    # 異常系: 名前なし
    with pytest.raises(ValidationError):
        await tool.execute({})
    
    # 異常系: 名前が長すぎる
    with pytest.raises(ValueError):
        await tool.execute({"name": "a" * 51})


@pytest.mark.asyncio
async def test_add_tool():
    """AddToolのテスト"""
    tool = AddTool()
    
    # 正常系: 整数
    result = await tool.execute({"a": 5, "b": 3})
    assert "8" in result[0].text
    
    # 正常系: 浮動小数点
    result = await tool.execute({"a": 1.5, "b": 2.5})
    assert "4.0" in result[0].text
    
    # 異常系: パラメータ不足
    with pytest.raises(ValidationError):
        await tool.execute({"a": 5})


@pytest.mark.asyncio
async def test_get_time_tool():
    """GetTimeToolのテスト"""
    tool = GetTimeTool()
    
    # 正常系
    result = await tool.execute({})
    assert len(result) == 1
    assert "現在の日時" in result[0].text
    assert "年" in result[0].text
    assert "月" in result[0].text
    assert "日" in result[0].text


def test_tool_definitions():
    """ツール定義のテスト"""
    hello = HelloTool()
    add = AddTool()
    time = GetTimeTool()
    
    # 名前の確認
    assert hello.name == "hello"
    assert add.name == "add"
    assert time.name == "get_time"
    
    # スキーマの確認
    assert "name" in hello.input_schema["properties"]
    assert "a" in add.input_schema["properties"]
    assert "b" in add.input_schema["properties"]