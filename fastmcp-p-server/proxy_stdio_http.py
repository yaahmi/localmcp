#!/usr/bin/env python3
"""
完全版 SSE stdio プロキシ
Claude Desktop (stdio) ↔ MCP SSE Server

重要: 1つのSSE接続を維持し続ける実装
"""
import sys
import json
import asyncio
import httpx
from httpx_sse import aconnect_sse
from typing import Optional, Dict, Any


class SSEStdioProxy:
    """stdio と SSE の間を中継するプロキシ"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session_id: Optional[str] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.running = True
        self.sse_connected = False
        self.stdin_queue = asyncio.Queue()
        self.stdout_queue = asyncio.Queue()
        
    def log(self, message: str):
        """ログを標準エラー出力に出力"""
        print(f"[SSE Proxy] {message}", file=sys.stderr, flush=True)
    
    async def sse_event_listener(self):
        """
        SSEイベントをリッスン
        1つの接続を維持し続ける
        """
        try:
            sse_url = f"{self.server_url}/sse"
            self.log(f"Connecting to SSE stream: {sse_url}")
            
            async with aconnect_sse(
                self.http_client,
                "GET",
                sse_url
            ) as event_source:
                
                self.log("SSE connection established")
                
                async for event in event_source.aiter_sse():
                    if not self.running:
                        break
                    
                    if event.event == "connected":
                        # 接続確立
                        data = json.loads(event.data)
                        self.session_id = data["session_id"]
                        self.sse_connected = True
                        self.log(f"Received session_id: {self.session_id}")
                    
                    elif event.event == "message":
                        # メッセージ受信
                        data = json.loads(event.data)
                        self.log(f"Received message: {data.get('method', data.get('id'))}")
                        
                        # stdoutキューに追加
                        await self.stdout_queue.put(data)
                    
                    elif event.event == "ping":
                        # キープアライブ
                        pass
                    
        except Exception as e:
            self.log(f"SSE listener error: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            self.sse_connected = False
            self.running = False
    
    async def stdin_reader(self):
        """標準入力を読み取る"""
        try:
            loop = asyncio.get_event_loop()
            
            while self.running:
                try:
                    # 標準入力から1行読み取る
                    line = await loop.run_in_executor(None, sys.stdin.readline)
                    
                    if not line:
                        self.log("End of input (stdin closed)")
                        self.running = False
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    # JSONをパース
                    message = json.loads(line)
                    self.log(f"Read from stdin: {message.get('method', 'response')}")
                    
                    # stdinキューに追加
                    await self.stdin_queue.put(message)
                    
                except json.JSONDecodeError as e:
                    self.log(f"JSON decode error: {e}")
                except Exception as e:
                    self.log(f"Error reading stdin: {e}")
                    
        except Exception as e:
            self.log(f"stdin_reader error: {e}")
            self.running = False
    
    async def stdout_writer(self):
        """標準出力に書き込む"""
        try:
            while self.running:
                try:
                    # タイムアウト付きでキューから取得
                    message = await asyncio.wait_for(
                        self.stdout_queue.get(),
                        timeout=1.0
                    )
                    
                    # JSONを標準出力に書き込む
                    json_str = json.dumps(message)
                    print(json_str, flush=True)
                    self.log(f"Wrote to stdout: {message.get('id', 'notification')}")
                    
                except asyncio.TimeoutError:
                    # タイムアウト（正常）
                    continue
                except Exception as e:
                    self.log(f"Error writing to stdout: {e}")
                    
        except Exception as e:
            self.log(f"stdout_writer error: {e}")
    
    async def message_forwarder(self):
        """
        stdinキューからメッセージを取得してサーバーに転送
        """
        try:
            # SSE接続が確立されるまで待つ
            for _ in range(100):  # 10秒待つ
                if self.sse_connected and self.session_id:
                    break
                await asyncio.sleep(0.1)
            
            if not self.sse_connected:
                self.log("Failed to establish SSE connection")
                self.running = False
                return
            
            self.log("Message forwarder ready")
            
            while self.running:
                try:
                    # タイムアウト付きでキューから取得
                    message = await asyncio.wait_for(
                        self.stdin_queue.get(),
                        timeout=1.0
                    )
                    
                    # サーバーに転送
                    await self.send_to_server(message)
                    
                except asyncio.TimeoutError:
                    # タイムアウト（正常）
                    continue
                except Exception as e:
                    self.log(f"Error forwarding message: {e}")
                    
        except Exception as e:
            self.log(f"message_forwarder error: {e}")
    
    async def send_to_server(self, message: Dict[str, Any]):
        """サーバーにメッセージを送信"""
        try:
            # session_idをヘッダーに追加
            headers = {
                "X-Session-Id": self.session_id,
                "Content-Type": "application/json"
            }
            
            self.log(f"Sending to server: {message.get('method', 'response')}")
            
            # メッセージを送信
            response = await self.http_client.post(
                f"{self.server_url}/messages",
                json=message,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"Server accepted: {result.get('status')}")
            else:
                self.log(f"Server error: {response.status_code}")
                self.log(f"Response: {response.text}")
                
                # エラーレスポンスを生成
                error_response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32000,
                        "message": f"Server error: {response.status_code}"
                    }
                }
                await self.stdout_queue.put(error_response)
            
        except Exception as e:
            self.log(f"Error sending to server: {e}")
            
            # エラーレスポンスを生成
            error_response = {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Proxy error: {str(e)}"
                }
            }
            await self.stdout_queue.put(error_response)
    
    async def run(self):
        """プロキシのメインループ"""
        try:
            # HTTPクライアントを作成
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            self.log("Starting SSE stdio proxy")
            self.log(f"Server URL: {self.server_url}")
            
            # 4つのタスクを並行実行
            tasks = [
                asyncio.create_task(self.sse_event_listener(), name="sse_listener"),
                asyncio.create_task(self.stdin_reader(), name="stdin_reader"),
                asyncio.create_task(self.stdout_writer(), name="stdout_writer"),
                asyncio.create_task(self.message_forwarder(), name="message_forwarder")
            ]
            
            self.log("All tasks started")
            
            # いずれかのタスクが終了するまで待つ
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED
            )
            
            self.log("A task completed, shutting down")
            self.running = False
            
            # 残りのタスクをキャンセル
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # 完了したタスクの例外を確認
            for task in done:
                if task.exception():
                    self.log(f"Task {task.get_name()} failed: {task.exception()}")
            
        except KeyboardInterrupt:
            self.log("Interrupted")
        except Exception as e:
            self.log(f"Error: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
        finally:
            self.running = False
            if self.http_client:
                await self.http_client.aclose()
            self.log("Proxy stopped")


async def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SSE stdio proxy for MCP")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8999",
        help="SSE server URL (default: http://127.0.0.1:8999)"
    )
    
    args = parser.parse_args()
    
    proxy = SSEStdioProxy(args.url)
    await proxy.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SSE Proxy] Stopped", file=sys.stderr)