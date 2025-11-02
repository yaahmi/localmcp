# Hello World MCP Server

FastMCPサーバーのSSE実装版です

## セットアップ

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

## 従来のHTTP vs SSE
【従来のHTTP】
Client ─────Request────────> Server
Client <────Response──────── Server
（1回のやり取りで終了）

【WebSocket】
Client <═══双方向通信═══> Server
（複雑なプロトコル、維持コストが高い）

【SSE】
Client ─────Request────────> Server （接続確立）
Client <──────┐
Client <──────┤ イベント
Client <──────┤ ストリーム
Client <──────┤ (継続)
Client <──────┘
（シンプルで軽量、サーバー→クライアントの一方向）
SSEの特徴
✅ シンプル: 標準HTTPの上で動作
✅ 軽量: WebSocketより低オーバーヘッド
✅ 自動再接続: ブラウザが自動的に再接続
✅ テキストベース: デバッグが容易
❌ 一方向: サーバー→クライアントのみ（クライアント→サーバーは別途POST）

## アーキテクチャ図（完全版）
```
Claude Desktop
    │
    │ stdio (JSON-RPC)
    ↓
┌─────────────────────────────────────────┐
│  SSE stdio Proxy                        │
│  ┌──────────────────────────────────┐  │
│  │ stdin_reader  → stdin_queue      │  │
│  │ message_forwarder → POST         │  │
│  │ sse_listener  ← SSE stream       │  │
│  │ stdout_writer ← stdout_queue     │  │
│  └──────────────────────────────────┘  │
└────────┬──────────────────┬────────────┘
         │                  │
         │ POST /messages   │ GET /sse
         │ (session_id)     │ (1つの接続維持)
         ↓                  ↓
┌─────────────────────────────────────────┐
│  MCP SSE Server                         │
│  - GET /sse → session_id発行             │
│  - POST /messages → 処理                 │
│  - SSE stream → レスポンス送信            │
└─────────────────────────────────────────┘

## SSE接続の正しい流れ
```
クライアント                    サーバー
    │                              │
    │ ① GET /sse                   │
    ├──────────────────────────────>│
    │                              │ ② session_id発行
    │ ③ event: connected           │    (active_connections登録)
    │<──────────────────────────────┤
    │                              │
    │ ④ POST /messages              │
    │    (session_id付き)           │
    ├──────────────────────────────>│
    │                              │ ⑤ session_idで検証
    │                              │    ✅ OK
    │                              │    pending_responses[session_id]
    │                              │       にレスポンスを追加
    │ ⑥ event: message             │
    │    (SSEストリーム経由)        │
    │<──────────────────────────────┤
    │                              │
    │ (同じ接続を維持)             │

## Claude Desktop設定

{
  "mcpServers": {
    "hello-world-http": {
      "command": "/Users/username/fastmcp-p-server/venv/bin/python",
      "args": ["/Users/username/fastmcp-p-server/src/proxy_stdio_http.py"],
      "env": {
        "PYTHONPATH": "/Users/username/fastmcp-p-server",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}


