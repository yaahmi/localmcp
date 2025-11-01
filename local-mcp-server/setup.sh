#!/bin/bash

echo "=== MCP Server Setup Script ==="
echo ""

# プロジェクトディレクトリを作成
PROJECT_DIR="hello-mcp-server"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  ディレクトリ $PROJECT_DIR は既に存在します"
    read -p "削除して再作成しますか？ (y/n): " answer
    if [ "$answer" = "y" ]; then
        rm -rf "$PROJECT_DIR"
    else
        echo "セットアップを中止しました"
        exit 1
    fi
fi

echo "📁 プロジェクトディレクトリを作成中..."
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# ディレクトリ構造を作成
echo "📁 ディレクトリ構造を作成中..."
mkdir -p config
mkdir -p src/core
mkdir -p src/tools
mkdir -p src/utils
mkdir -p tests

# 仮想環境を作成
echo "🐍 Python仮想環境を作成中..."
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存関係をインストール
echo "📦 依存パッケージをインストール中..."
pip install --upgrade pip
pip install mcp pyyaml pytest pytest-asyncio

echo ""
echo "✅ セットアップが完了しました！"
echo ""
echo "次のステップ:"
echo "1. このドキュメントから各ファイルの内容をコピーして配置してください"
echo "2. 仮想環境を有効化: source $PROJECT_DIR/venv/bin/activate"
echo "3. サーバーを起動: python src/server.py"
echo ""
echo "Claude Desktop設定ファイルの場所:"
echo "  ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "設定例:"
echo '{'
echo '  "mcpServers": {'
echo '    "hello-world": {'
echo "      \"command\": \"$(pwd)/venv/bin/python\","
echo "      \"args\": [\"$(pwd)/src/server.py\"]"
echo '    }'
echo '  }'
echo '}'
