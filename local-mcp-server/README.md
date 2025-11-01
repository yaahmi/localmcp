# Hello World MCP Server

プロダクションレベルのアーキテクチャを持つMCPサーバーのサンプル実装です。

## セットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/server.py
```

## Claude Desktop設定

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/src/server.py"]
    }
  }
}
```
