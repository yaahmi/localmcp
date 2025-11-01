# Hello World MCP Server

割としっかりめに作ったMCPサーバーのサンプル実装です。

## セットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x server.py
python src/server.py
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
      "args": ["/absolute/path/to/src/server.py"],
      "env": {
      "PYTHONPATH": "/absolute/path/to/"
        }
    }
  }
}
```
