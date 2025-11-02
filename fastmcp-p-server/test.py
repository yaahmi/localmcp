#!/usr/bin/env python3
"""
最終版 SSE MCPサーバーのテストクライアント
1つのSSE接続を維持する正しい実装
"""
import asyncio
import json
from typing import Optional, Dict, Any
import httpx
from httpx_sse import aconnect_sse


class MCPSSETestClient:
    """MCP SSEサーバーのテストクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:8999"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.responses = {}
        self.request_id = 0
        self.sse_connected = False
    
    def print_section(self, title: str):
        """セクションヘッダーを表示"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    
    def print_step(self, step: str, detail: str = ""):
        """ステップを表示"""
        print(f"\n▶ {step}")
        if detail:
            print(f"  {detail}")
    
    def get_next_id(self) -> int:
        """次のリクエストIDを取得"""
        self.request_id += 1
        return self.request_id
    
    async def test_health(self):
        """ヘルスチェックのテスト"""
        self.print_section("1. ヘルスチェック")
        
        self.print_step("GET /health を実行")
        
        try:
            response = await self.http_client.get(f"{self.base_url}/health")
            
            print(f"  ステータス: {response.status_code}")
            data = response.json()
            print(f"  サービス: {data.get('service')}")
            print(f"  状態: {data.get('status')}")
            print(f"  トランスポート: {data.get('transport')}")
            print(f"  アクティブ接続: {data.get('active_connections')}")
            
            return response.status_code == 200
        except Exception as e:
            print(f"  ❌ エラー: {e}")
            return False
    
    async def sse_event_listener(self):
        """
        SSEイベントをリッスンするバックグラウンドタスク
        これが1つのSSE接続を維持し続ける
        """
        try:
            sse_url = f"{self.base_url}/sse"
            
            self.print_step("GET /sse でSSEストリームに接続中...")
            print("  これがSSEの最初のステップです")
            print("  サーバーは接続を保持し、イベントをプッシュします")
            
            async with aconnect_sse(
                self.http_client,
                "GET",
                sse_url
            ) as event_source:
                
                self.print_step("接続確立イベントを待機中...")
                
                async for event in event_source.aiter_sse():
                    print(f"  イベントタイプ: {event.event}")
                    
                    if event.event == "connected":
                        # 接続確立
                        data = json.loads(event.data)
                        self.session_id = data["session_id"]
                        self.sse_connected = True
                        
                        print(f"  データ: {event.data}")
                        print(f"\n  ✅ 接続成功!")
                        print(f"  📝 Session ID: {self.session_id}")
                        print(f"\n  このSession IDを使って、POST /messages でリクエストを送信します")
                        print(f"\n  📡 SSEイベントリスナー起動")
                        print(f"  サーバーからのレスポンスを待機します...\n")
                    
                    elif event.event == "message":
                        # メッセージ受信
                        data = json.loads(event.data)
                        request_id = data.get("id")
                        
                        print(f"\n  📨 SSE経由でレスポンス受信 (ID: {request_id})")
                        
                        if "result" in data:
                            print(f"  ✅ 成功")
                            if "tools" in data["result"]:
                                tools = data["result"]["tools"]
                                print(f"  ツール数: {len(tools)}")
                            elif "content" in data["result"]:
                                content = data["result"]["content"][0]["text"]
                                print(f"  レスポンス: {content[:100]}...")
                        elif "error" in data:
                            print(f"  ❌ エラー: {data['error']['message']}")
                        
                        # レスポンスを保存
                        self.responses[request_id] = data
                    
                    elif event.event == "ping":
                        # キープアライブ
                        print("  💓 キープアライブ (ping)")
                        
        except Exception as e:
            print(f"\n  ❌ SSEリスナーエラー: {e}")
            import traceback
            traceback.print_exc()
            self.sse_connected = False
    
    async def wait_for_connection(self, timeout: int = 5):
        """SSE接続が確立されるまで待つ"""
        for _ in range(timeout * 10):
            if self.sse_connected and self.session_id:
                return True
            await asyncio.sleep(0.1)
        return False
    
    async def send_request(self, request: dict, timeout: int = 10) -> dict:
        """リクエストを送信"""
        try:
            # session_idをヘッダーに追加
            headers = {
                "X-Session-Id": self.session_id,
                "Content-Type": "application/json"
            }
            
            response = await self.http_client.post(
                f"{self.base_url}/messages",
                json=request,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ リクエスト受付: {result.get('status')}")
                
                # レスポンスを待つ
                request_id = request["id"]
                for _ in range(timeout * 10):
                    if request_id in self.responses:
                        return self.responses[request_id]
                    await asyncio.sleep(0.1)
                
                print(f"  ⚠️  レスポンスタイムアウト")
                return None
            else:
                print(f"  ❌ サーバーエラー: {response.status_code}")
                print(f"  レスポンス: {response.text}")
                return None
        
        except Exception as e:
            print(f"  ❌ 送信エラー: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def test_list_tools(self):
        """ツール一覧の取得テスト"""
        self.print_section("3. ツール一覧の取得")
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": self.get_next_id()
        }
        
        self.print_step("POST /messages でリクエスト送信")
        print(f"  Session ID: {self.session_id}")
        print(f"  リクエスト: {json.dumps(request, ensure_ascii=False)}")
        
        response = await self.send_request(request)
        
        if response and "result" in response:
            tools = response["result"]["tools"]
            print(f"\n  📋 利用可能なツール ({len(tools)}個):")
            for tool in tools:
                print(f"    - {tool['name']}: {tool['description']}")
            return True
        
        return False
    
    async def test_call_hello(self):
        """helloツールの実行テスト"""
        self.print_section("4. helloツールの実行")
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "hello",
                "arguments": {"name": "太郎"}
            },
            "id": self.get_next_id()
        }
        
        self.print_step("helloツールを実行")
        print(f"  パラメータ: name='太郎'")
        
        response = await self.send_request(request)
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"\n  💬 レスポンス:")
            print(f"  {content}")
            return True
        
        return False
    
    async def test_call_add(self):
        """addツールの実行テスト"""
        self.print_section("5. addツールの実行")
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {"a": 123, "b": 456}
            },
            "id": self.get_next_id()
        }
        
        self.print_step("addツールを実行")
        print(f"  パラメータ: a=123, b=456")
        
        response = await self.send_request(request)
        
        if response and "result" in response:
            content = response["result"]["content"][0]["text"]
            print(f"\n  🔢 計算結果:")
            print(f"  {content}")
            return True
        
        return False
    
    async def run_all_tests(self):
        """すべてのテストを実行"""
        print("""
╔════════════════════════════════════════════════════════════╗
║  MCP SSE Server - Test Client                              ║
╠════════════════════════════════════════════════════════════╣
║  SSE (Server-Sent Events) の動作を可視化します            ║
╚════════════════════════════════════════════════════════════╝

SSEの仕組み:
  1. クライアントがGET /sseでストリーム接続（維持）
  2. サーバーがsession_idを発行
  3. クライアントがPOST /messagesでリクエスト送信
  4. サーバーがSSEストリーム経由でレスポンス送信
  5. 【重要】接続は切断せず、同じストリームで継続
""")
        
        # HTTPクライアントを作成
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        try:
            # ヘルスチェック
            self.print_section("1. ヘルスチェック")
            health_ok = await self.test_health()
            
            if not health_ok:
                print("\n❌ ヘルスチェックが失敗しました")
                return
            
            self.print_section("2. SSEストリーム接続")
            
            # SSEイベントリスナーをバックグラウンドで起動
            # これが1つの接続を維持し続ける
            listener_task = asyncio.create_task(self.sse_event_listener())
            
            # 接続が確立されるまで待つ
            if not await self.wait_for_connection():
                print("\n❌ SSE接続がタイムアウトしました")
                listener_task.cancel()
                return
            
            # テストを実行
            tests = [
                ("ツール一覧取得", self.test_list_tools),
                ("helloツール実行", self.test_call_hello),
                ("addツール実行", self.test_call_add),
            ]
            
            results = [
                ("ヘルスチェック", True),
                ("SSE接続", True),
            ]
            
            for name, test_func in tests:
                try:
                    result = await test_func()
                    results.append((name, result))
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"\n❌ {name} でエラー: {e}")
                    import traceback
                    traceback.print_exc()
                    results.append((name, False))
            
            # リスナータスクをキャンセル
            listener_task.cancel()
            try:
                await listener_task
            except asyncio.CancelledError:
                pass
            
            # サマリー
            self.print_section("テスト結果サマリー")
            
            passed = sum(1 for _, result in results if result)
            total = len(results)
            
            for name, result in results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {status}: {name}")
            
            print(f"\n  合計: {passed}/{total} テスト成功")
            
            if passed == total:
                print("\n  🎉 すべてのテストが成功しました!")
                print("\n  SSEの仕組みを理解できましたか？")
                print("  - 1つの接続を維持")
                print("  - session_idで識別")
                print("  - リクエストはPOST、レスポンスはSSE")
            else:
                print(f"\n  ⚠️  {total - passed} 個のテストが失敗しました")
        
        finally:
            await self.http_client.aclose()


async def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP SSE Server")
    parser.add_argument(
        "--url",
        default="http://localhost:8999",
        help="Server URL"
    )
    
    args = parser.parse_args()
    
    client = MCPSSETestClient(args.url)
    await client.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n中断されました")