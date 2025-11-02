#!/usr/bin/env python3
"""
完全版 SSE MCPサーバー
Server-Sent Events を使用した双方向通信

SSE (Server-Sent Events) について:
- サーバーからクライアントへのリアルタイムプッシュ通信
- HTTP/HTTPSの標準プロトコル上で動作
- 自動再接続機能を持つ
- テキストベースのイベントストリーム

MCP over SSEの仕組み:
1. GET /sse - SSEストリームを確立（サーバー→クライアント）
2. POST /messages - リクエストを送信（クライアント→サーバー）
3. SSEストリーム経由でレスポンスを受信
"""
import sys
from pathlib import Path
from datetime import datetime
import asyncio
import json
from typing import Dict, Any, Optional
import uuid

# プロジェクトルートをPYTHONPATHに追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn

# FastAPIアプリケーション
app = FastAPI(title="MCP SSE Server", version="2.0.0")

# 接続管理
active_connections: Dict[str, asyncio.Queue] = {}
pending_responses: Dict[str, asyncio.Queue] = {}


# ========================================
# ツール実装
# ========================================

def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """ツールを実行"""
    
    if name == "hello":
        user_name = arguments.get("name", "名無し")
        if len(user_name) > 50:
            raise ValueError("名前は50文字以内にしてください")
        return f"こんにちは、{user_name}さん！🎉\nSSE経由のMCPサーバーから挨拶します。"
    
    elif name == "add":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        return f"計算結果: {a} + {b} = {result}"
    
    elif name == "multiply":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a * b
        return f"計算結果: {a} × {b} = {result}"
    
    elif name == "divide":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        if b == 0:
            raise ValueError("0で割ることはできません")
        result = a / b
        return f"計算結果: {a} ÷ {b} = {result}"
    
    elif name == "get_time":
        now = datetime.now()
        return f"現在の日時: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"
    
    elif name == "server_info":
        return """サーバー情報:
名前: hello-world-mcp
バージョン: 2.0.0
トランスポート: SSE (Server-Sent Events)
プロトコル: MCP over SSE/HTTP
エンドポイント:
  - GET /sse (SSEストリーム)
  - POST /messages (メッセージ送信)
  - GET /health (ヘルスチェック)"""
    
    else:
        raise ValueError(f"Unknown tool: {name}")


# ========================================
# MCPプロトコルハンドラ
# ========================================

def handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    """初期化リクエスト"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "prompts": {},
            "resources": {}
        },
        "serverInfo": {
            "name": "hello-world-mcp",
            "version": "2.0.0"
        }
    }


def handle_tools_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """ツール一覧"""
    return {
        "tools": [
            {
                "name": "hello",
                "description": "シンプルな挨拶を返します",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "挨拶する相手の名前"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "add",
                "description": "2つの数値を足し算します",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "1つ目の数値"},
                        "b": {"type": "number", "description": "2つ目の数値"}
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "multiply",
                "description": "2つの数値を掛け算します",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "divide",
                "description": "2つの数値を割り算します",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            },
            {
                "name": "get_time",
                "description": "現在の日時を返します",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "server_info",
                "description": "サーバー情報を返します",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    }


def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    """ツール実行"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    try:
        result = execute_tool(tool_name, arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": result
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"エラー: {str(e)}"
                }
            ],
            "isError": True
        }


def process_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """MCPリクエストを処理"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    try:
        if method == "initialize":
            result = handle_initialize(params)
        elif method == "tools/list":
            result = handle_tools_list(params)
        elif method == "tools/call":
            result = handle_tools_call(params)
        elif method == "prompts/list":
            result = {"prompts": []}
        elif method == "resources/list":
            result = {"resources": []}
        elif method == "notifications/initialized":
            # 通知は応答不要
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


# ========================================
# SSEエンドポイント
# ========================================

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "message": "MCP SSE Server",
        "version": "2.0.0",
        "transport": "SSE (Server-Sent Events)",
        "endpoints": {
            "sse_stream": "GET /sse",
            "send_message": "POST /messages",
            "health": "GET /health"
        },
        "description": "Server-Sent Eventsを使用したMCPサーバー"
    }


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "hello-world-mcp",
        "version": "2.0.0",
        "transport": "SSE",
        "active_connections": len(active_connections)
    }


@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    SSEストリームエンドポイント
    
    クライアントはこのエンドポイントに接続して、
    サーバーからのイベントをリアルタイムで受信します。
    """
    # セッションIDを生成
    session_id = str(uuid.uuid4())
    
    # このセッション用のキューを作成
    queue = asyncio.Queue()
    active_connections[session_id] = queue
    pending_responses[session_id] = asyncio.Queue()
    
    print(f"[SSE] New connection: {session_id}", flush=True)
    
    async def event_generator():
        """SSEイベントを生成"""
        try:
            # 接続確立イベントを送信
            yield {
                "event": "connected",
                "data": json.dumps({
                    "session_id": session_id,
                    "message": "SSE connection established"
                })
            }
            
            # キューからイベントを取得して送信
            while True:
                # クライアントの切断をチェック
                if await request.is_disconnected():
                    print(f"[SSE] Client disconnected: {session_id}", flush=True)
                    break
                
                try:
                    # タイムアウト付きでメッセージを待つ
                    message = await asyncio.wait_for(
                        pending_responses[session_id].get(),
                        timeout=30.0
                    )
                    
                    # メッセージをSSEイベントとして送信
                    yield {
                        "event": "message",
                        "data": json.dumps(message)
                    }
                    
                except asyncio.TimeoutError:
                    # キープアライブ（接続維持）
                    yield {
                        "event": "ping",
                        "data": json.dumps({"timestamp": datetime.now().isoformat()})
                    }
                
        except Exception as e:
            print(f"[SSE] Error in event generator: {e}", flush=True)
        
        finally:
            # クリーンアップ
            if session_id in active_connections:
                del active_connections[session_id]
            if session_id in pending_responses:
                del pending_responses[session_id]
            print(f"[SSE] Connection closed: {session_id}", flush=True)
    
    return EventSourceResponse(event_generator())


@app.post("/messages")
async def messages_endpoint(request: Request):
    """
    メッセージ送信エンドポイント
    
    クライアントはこのエンドポイントにMCPリクエストを送信します。
    レスポンスはSSEストリーム経由で返されます。
    """
    try:
        body = await request.json()
        
        # セッションIDを取得（ヘッダーまたはボディから）
        session_id = request.headers.get("X-Session-Id") or body.get("_session_id")
        
        if not session_id or session_id not in pending_responses:
            return JSONResponse(
                content={
                    "error": "Invalid or missing session_id",
                    "hint": "Connect to /sse first to establish a session"
                },
                status_code=400
            )
        
        print(f"[Messages] Received request from {session_id}: {body.get('method')}", flush=True)
        
        # MCPリクエストを処理
        response = process_mcp_request(body)
        
        # レスポンスをSSEキューに追加
        if response:
            await pending_responses[session_id].put(response)
        
        # 受信確認を返す
        return JSONResponse(
            content={
                "status": "queued",
                "message": "Response will be sent via SSE stream"
            }
        )
    
    except Exception as e:
        print(f"[Messages] Error: {e}", flush=True)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


# ========================================
# メイン処理
# ========================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP SSE Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8999, help="Port to bind")
    
    args = parser.parse_args()
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  MCP SSE Server Started                                    ║
╠════════════════════════════════════════════════════════════╣
║  SSE Stream:  http://{args.host}:{args.port}/sse              ║
║  Messages:    http://{args.host}:{args.port}/messages        ║
║  Health:      http://{args.host}:{args.port}/health          ║
╠════════════════════════════════════════════════════════════╣
║  SSE (Server-Sent Events) について                        ║
║  ────────────────────────────────────────────             ║
║  1. GET /sse でストリーム接続を確立                        ║
║  2. session_idを取得                                       ║
║  3. POST /messages でリクエスト送信                        ║
║  4. SSEストリーム経由でレスポンス受信                      ║
╚════════════════════════════════════════════════════════════╝

依存関係:
  pip install fastapi uvicorn sse-starlette

テスト方法:
  python test_sse_client.py

終了するには Ctrl+C を押してください
""")
    
    try:
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nサーバーを停止しました")