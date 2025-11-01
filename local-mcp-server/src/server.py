#!/usr/bin/env python3
"""
MCPサーバーのエントリーポイント
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src.core.registry import ToolRegistry
from src.core.exceptions import MCPToolError
from src.tools.hello import HelloTool
from src.tools.math import AddTool
from src.tools.time import GetTimeTool
from src.utils.logger import StructuredLogger

# ロガーの初期化
logger = StructuredLogger("server")

# サーバーインスタンスの作成
app = Server("hello-world-mcp")

# ツールレジストリの作成と登録
registry = ToolRegistry()
registry.register_multiple([
    HelloTool(),
    AddTool(),
    GetTimeTool(),
])


@app.list_tools()
async def list_tools() -> list[Tool]:
    """ツール一覧を返す"""
    return registry.get_all_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """ツールを実行"""
    try:
        return await registry.execute_tool(name, arguments)
    except MCPToolError as e:
        logger.error("MCP Tool Error", error=e)
        return [TextContent(
            type="text",
            text=f"エラー: {str(e)}"
        )]
    except Exception as e:
        logger.error("Unexpected Error", error=e)
        return [TextContent(
            type="text",
            text=f"予期しないエラーが発生しました: {str(e)}"
        )]


async def main():
    """メイン処理"""
    logger.info("MCP Server starting")
    logger.info(f"Registered tools: {registry.list_tool_names()}")
    
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server connected via stdio")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server crashed", error=e)
        raise