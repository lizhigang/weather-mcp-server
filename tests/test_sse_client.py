"""SSE 模式 MCP 客户端测试工具"""

import json
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import urljoin
from threading import Thread


def read_sse_events(response, event_handler, timeout=30):
    """在后台线程读取 SSE 事件"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            line = response.readline().decode('utf-8').strip()
            if line:
                event_handler(line)
        except:
            break


def test_sse_mode(base_url: str = "http://localhost:8080"):
    """测试 SSE 模式的 MCP 服务器"""
    
    print("=" * 50)
    print("SSE 模式 MCP 服务器测试")
    print("=" * 50)
    
    responses = {}
    
    def handle_event(line):
        """处理 SSE 事件"""
        print(f"  [SSE] {line}")
        if line.startswith("data:"):
            try:
                data = json.loads(line[5:].strip())
                if "id" in data:
                    responses[data["id"]] = data
            except:
                pass
    
    # 1. 建立 SSE 连接
    print("\n[1] 连接到 SSE 端点...")
    sse_url = urljoin(base_url, "/sse")
    
    try:
        req = urllib.request.Request(
            sse_url,
            headers={"Accept": "text/event-stream"}
        )
        
        sse_response = urllib.request.urlopen(req, timeout=10)
        print(f"✓ SSE 连接成功 (状态: {sse_response.status})")
        print(f"  内容类型: {sse_response.headers.get('Content-Type')}")
        
        # 读取 endpoint 信息
        session_id = None
        endpoint_path = None
        for _ in range(10):
            line = sse_response.readline().decode('utf-8').strip()
            print(f"  收到: {line}")
            
            if line.startswith("data:") and endpoint_path is None:
                endpoint_path = line[5:].strip()
                print(f"✓ 获取到 endpoint: {endpoint_path}")
                if "session_id=" in endpoint_path:
                    session_id = endpoint_path.split("session_id=")[1]
                    print(f"✓ 获取到 session_id: {session_id}")
                    break
            
            if line == "":
                continue
        
        if not session_id:
            print("✗ 未能获取 session_id")
            return
            
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return
    
    # 启动后台线程读取 SSE 事件
    sse_thread = Thread(target=read_sse_events, args=(sse_response, handle_event, 60))
    sse_thread.daemon = True
    sse_thread.start()
    
    messages_url = urljoin(base_url, endpoint_path)
    
    # 2. 发送 initialize 请求
    print("\n[2] 发送 initialize 请求...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    try:
        req = urllib.request.Request(
            messages_url,
            data=json.dumps(init_request).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"  POST 状态: {response.status}")
    except Exception as e:
        print(f"✗ Initialize POST 失败: {e}")
    
    # 等待响应
    time.sleep(1)
    if 1 in responses:
        print(f"✓ Initialize 响应: {json.dumps(responses[1], indent=2, ensure_ascii=False)[:200]}...")
    else:
        print("✗ 未收到 Initialize 响应")
    
    # 3. 发送 tools/list 请求
    print("\n[3] 发送 tools/list 请求...")
    tools_request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    
    try:
        req = urllib.request.Request(
            messages_url,
            data=json.dumps(tools_request).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"  POST 状态: {response.status}")
    except Exception as e:
        print(f"✗ Tools/list POST 失败: {e}")
    
    # 等待响应
    time.sleep(1)
    if 2 in responses:
        result = responses[2]
        print(f"✓ Tools 列表:")
        if "result" in result and "tools" in result["result"]:
            for tool in result["result"]["tools"]:
                print(f"  - {tool['name']}: {tool.get('description', 'N/A')[:40]}...")
    else:
        print("✗ 未收到 Tools/list 响应")
    
    # 4. 测试 tool call
    print("\n[4] 测试调用 get_current_weather_tool...")
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_current_weather_tool",
            "arguments": {"city": "Beijing"}
        }
    }
    
    try:
        req = urllib.request.Request(
            messages_url,
            data=json.dumps(call_request).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"  POST 状态: {response.status}")
    except Exception as e:
        print(f"✗ Tool call POST 失败: {e}")
    
    # 等待响应
    time.sleep(1)
    if 3 in responses:
        result = responses[3]
        print(f"✓ Tool call 响应:")
        if "result" in result and "content" in result["result"]:
            for item in result["result"]["content"]:
                if item.get("type") == "text":
                    try:
                        weather_data = json.loads(item.get("text", "{}"))
                        print(f"  城市: {weather_data.get('city')}")
                        print(f"  温度: {weather_data.get('temperature_celsius')}°C")
                        print(f"  天气: {weather_data.get('conditions')}")
                        print(f"  湿度: {weather_data.get('humidity_percent')}%")
                    except Exception as e:
                        print(f"  内容: {item.get('text', 'N/A')[:100]}")
    else:
        print("✗ 未收到 Tool call 响应")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    test_sse_mode(base_url)
