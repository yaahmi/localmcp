# Hello World MCP Server

FastMCPサーバーのサンプル実装です。

## セットアップ

```bash

source venv/bin/activate
pip install -r requirements.txt
python server_fastmcp.py
```
## Pythonパスを確認
```
echo $PYTHONPATH

# プロジェクトルートをPythonパスに追加
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Claude Desktop設定

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "hello-world": {
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/server_fastmcp.py"],
      "env": {
      "PYTHONPATH": "/absolute/path/to/"
      "PYTHONUNBUFFERED": "1"
        }
    }
  }
}
```

