#!/usr/bin/env python3
"""
FastMCP版 MCPサーバー - シンプル完全版
クラス不要、関数だけで全て実装
"""
from fastmcp import FastMCP
from datetime import datetime
from typing import Optional

# サーバーの作成（これだけ！）
mcp = FastMCP("hello-world-mcp")


# ========================================
# Tools - 普通の関数を書くだけ
# ========================================

@mcp.tool()
def hello(name: str) -> str:
    """
    シンプルな挨拶を返します
    
    Args:
        name: 挨拶する相手の名前（50文字以内）
    
    Returns:
        挨拶メッセージ
    
    Raises:
        ValueError: 名前が50文字を超える場合
    """
    if len(name) > 50:
        raise ValueError("名前は50文字以内にしてください")
    
    return f"こんにちは、{name}さん！🎉\nMCPサーバーから挨拶します。"


@mcp.tool()
def add(a: float, b: float) -> str:
    """
    2つの数値を足し算します
    
    Args:
        a: 1つ目の数値
        b: 2つ目の数値
    
    Returns:
        計算結果を含むメッセージ
    """
    result = a + b
    return f"計算結果: {a} + {b} = {result}"


@mcp.tool()
def subtract(a: float, b: float) -> str:
    """2つの数値を引き算します"""
    result = a - b
    return f"計算結果: {a} - {b} = {result}"


@mcp.tool()
def multiply(a: float, b: float) -> str:
    """2つの数値を掛け算します"""
    result = a * b
    return f"計算結果: {a} × {b} = {result}"


@mcp.tool()
def divide(a: float, b: float) -> str:
    """
    2つの数値を割り算します
    
    Args:
        a: 割られる数
        b: 割る数
    
    Returns:
        計算結果
    
    Raises:
        ValueError: bが0の場合
    """
    if b == 0:
        raise ValueError("0で割ることはできません")
    
    result = a / b
    return f"計算結果: {a} ÷ {b} = {result}"


@mcp.tool()
def get_time() -> str:
    """現在の日時を返します"""
    now = datetime.now()
    return f"現在の日時: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"


@mcp.tool()
def greet_multiple(names: list[str], greeting: str = "こんにちは") -> str:
    """
    複数の人に挨拶します
    
    Args:
        names: 挨拶する人のリスト
        greeting: 使用する挨拶（デフォルト: "こんにちは"）
    
    Returns:
        全員への挨拶メッセージ
    """
    if not names:
        return "挨拶する相手がいません"
    
    greetings = [f"{greeting}、{name}さん！" for name in names]
    return "\n".join(greetings)


@mcp.tool()
def calculate_age(birth_year: int) -> str:
    """
    生まれ年から年齢を計算します
    
    Args:
        birth_year: 生まれ年（西暦）
    
    Returns:
        年齢を含むメッセージ
    """
    current_year = datetime.now().year
    age = current_year - birth_year
    
    if age < 0:
        raise ValueError("未来の年が指定されています")
    
    return f"{birth_year}年生まれの方は、現在{age}歳です"


@mcp.tool()
def format_text(
    text: str,
    uppercase: bool = False,
    add_emoji: bool = False
) -> str:
    """
    テキストをフォーマットします
    
    Args:
        text: フォーマットするテキスト
        uppercase: 大文字に変換するか（デフォルト: False）
        add_emoji: 絵文字を追加するか（デフォルト: False）
    
    Returns:
        フォーマット済みテキスト
    """
    result = text
    
    if uppercase:
        result = result.upper()
    
    if add_emoji:
        result = f"✨ {result} ✨"
    
    return result


# ========================================
# Prompts - プロンプトテンプレート
# ========================================

@mcp.prompt()
def greeting_template(name: str, style: str = "casual") -> str:
    """
    挨拶メッセージのテンプレート
    
    Args:
        name: 挨拶する相手の名前
        style: 挨拶のスタイル（formal/casual）
    """
    if style == "formal":
        return f"""{name}様

お世話になっております。
本日はどのようなご用件でしょうか？

よろしくお願いいたします。"""
    else:
        return f"""こんにちは、{name}さん！👋

今日は何をお手伝いしましょうか？
気軽に聞いてくださいね！"""


@mcp.prompt()
def code_review(language: str, code: str) -> str:
    """
    コードレビュー用のプロンプトテンプレート
    
    Args:
        language: プログラミング言語
        code: レビューするコード
    """
    return f"""以下の{language}コードをレビューしてください：

```{language.lower()}
{code}
```

以下の観点でレビューをお願いします：
1. コードの品質と可読性
2. パフォーマンスの問題点
3. セキュリティの懸念事項
4. ベストプラクティスへの準拠
5. 具体的な改善提案
"""


@mcp.prompt()
def meeting_agenda(
    title: str,
    participants: list[str],
    topics: list[str]
) -> str:
    """
    会議のアジェンダを作成します
    
    Args:
        title: 会議のタイトル
        participants: 参加者のリスト
        topics: 議題のリスト
    """
    participants_text = "\n".join([f"- {p}" for p in participants])
    topics_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(topics)])
    
    return f"""# {title}

## 参加者
{participants_text}

## 議題
{topics_text}

## 準備事項
- 各自、事前に関連資料を確認してください
- 質問や懸念事項があれば事前に共有してください
"""


# ========================================
# Resources - リソース提供
# ========================================

@mcp.resource("config://server_info")
def get_server_info() -> str:
    """サーバー情報と統計"""
    import json
    info = {
        "name": "hello-world-mcp",
        "version": "2.0.0",
        "framework": "FastMCP",
        "python_version": "3.x",
        "tools_count": 9,
        "status": "running",
        "features": {
            "tools": True,
            "prompts": True,
            "resources": True
        }
    }
    return json.dumps(info, ensure_ascii=False, indent=2)


@mcp.resource("doc://readme")
def get_readme() -> str:
    """使い方ガイド"""
    return """# Hello World MCP Server (FastMCP版)

## 概要
FastMCPを使用したシンプルで直感的なMCPサーバー実装です。
クラス定義不要で、普通の関数を書くだけでツールを作成できます。

## 利用可能なツール

### 基本ツール
- **hello**: 挨拶を返します
- **get_time**: 現在の日時を返します
- **greet_multiple**: 複数の人に挨拶します

### 計算ツール
- **add**: 足し算
- **subtract**: 引き算
- **multiply**: 掛け算
- **divide**: 割り算

### ユーティリティ
- **calculate_age**: 年齢計算
- **format_text**: テキストフォーマット

## 使用例

```
"helloツールで太郎に挨拶して"
"addツールで5と3を足して"
"divideツールで100を4で割って"
"calculate_ageで1990年生まれの年齢を教えて"
```

## FastMCPの利点

✅ クラス定義不要
✅ 型ヒントから自動でスキーマ生成
✅ 自動的な型チェック
✅ シンプルなエラーハンドリング
✅ 最小限のコード量

## 開発者向け

新しいツールを追加するには、関数を書いて@mcp.tool()デコレータをつけるだけ：

```python
@mcp.tool()
def my_new_tool(param: str) -> str:
    '''ツールの説明'''
    return f"結果: {param}"
```

たったこれだけで、完全に動作するツールが完成します！
"""


@mcp.resource("doc://examples")
def get_examples() -> str:
    """実行例集"""
    return """# 実行例集

## 基本的な使い方

### 1. 挨拶ツール
```
ユーザー: "helloツールで田中さんに挨拶して"
結果: "こんにちは、田中さん！🎉
MCPサーバーから挨拶します。"
```

### 2. 計算ツール
```
ユーザー: "addツールで123と456を足して"
結果: "計算結果: 123 + 456 = 579"

ユーザー: "divideツールで100を3で割って"
結果: "計算結果: 100 ÷ 3 = 33.333..."
```

### 3. 複数人への挨拶
```
ユーザー: "greet_multipleツールで太郎、花子、次郎におはようと挨拶して"
結果: 
"おはよう、太郎さん！
おはよう、花子さん！
おはよう、次郎さん！"
```

### 4. テキストフォーマット
```
ユーザー: "format_textツールでhelloを大文字にして絵文字も追加して"
結果: "✨ HELLO ✨"
```

## プロンプトの使用例

### 会議アジェンダ作成
```
ユーザー: "meeting_agendaプロンプトで「四半期レビュー」という会議の
アジェンダを作って。参加者は山田、佐藤、鈴木で、議題は売上報告、
次期計画、課題の3つ"
```

## エラーハンドリングの例

```
ユーザー: "divideツールで10を0で割って"
結果: "エラー: 0で割ることはできません"
```
"""


# ========================================
# メイン処理
# ========================================

if __name__ == "__main__":
    # サーバーが起動！
    mcp.run()