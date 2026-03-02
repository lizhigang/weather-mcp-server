# Weather MCP Server

一个基于 MCP (Model Context Protocol) 协议的模拟天气服务，提供城市天气查询和天气预报功能。

## 功能特性

- **获取当前天气**: 查询指定城市的实时天气信息（温度、湿度、风速、天气状况等）
- **天气预报**: 获取未来 1-7 天的天气预报
- **支持城市列表**: 查看所有支持的城市及其坐标信息

## 安装

在项目根目录（`pyproject.toml` 所在目录）执行：

```bash
# 使用 uv 安装
uv pip install -e .

# 或使用 pip 安装
pip install -e .
```

> **注意**：`-e` 表示可编辑模式，安装后**不能删除 `src` 目录**，因为 Python 是通过链接直接引用源码的。

## 环境激活

使用命令前需要先激活虚拟环境：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

激活后可直接使用 `weather-mcp` 命令。或在未激活时使用完整路径：

```bash
# 不激活环境，直接调用
.venv\Scripts\weather-mcp.exe --help
# 或
.venv\Scripts\python.exe -m weather_mcp.server --help
```

## 使用方法

本服务支持三种 transport 模式运行：

### 1. stdio 模式（默认）

stdio 模式通过标准输入输出进行通信，适用于本地 AI 助手集成（如 Claude Desktop、Qoder 等）。

```bash
# 默认启动 stdio 模式
weather-mcp

# 或显式指定
weather-mcp --transport stdio
```

#### stdio 模式集成配置

在 Qoder 的 `mcp.json` 中配置（**使用虚拟环境中的 Python**）：

```json
{
  "mcpServers": {
    "weather": {
      "command": "/path/to/your/project/.venv/Scripts/python.exe",
      "args": ["-m", "weather_mcp.server"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

或使用生成的 CLI（如果已安装）：

```json
{
  "mcpServers": {
    "weather": {
      "command": "/path/to/your/project/.venv/Scripts/weather-mcp.exe",
      "args": [],
      "cwd": "/path/to/your/project"
    }
  }
}
```

在 Claude Desktop 的 `claude_desktop_config.json` 中配置：

```json
{
  "mcpServers": {
    "weather": {
      "command": "/path/to/your/project/.venv/Scripts/python.exe",
      "args": ["-m", "weather_mcp.server"]
    }
  }
}
```

> **提示**：将 `/path/to/your/project` 替换为你的实际项目路径。配置中使用虚拟环境的完整路径，无需手动激活环境。

### 2. streamable-http 模式

streamable-http 模式作为独立服务器运行，支持远程访问和多客户端连接，使用流式 HTTP 传输。

```bash
# 使用默认配置启动（host: 0.0.0.0, port: 8080）
weather-mcp --transport streamable-http

# 自定义主机和端口
weather-mcp --transport streamable-http --host 127.0.0.1 --port 3000
```

#### streamable-http 模式集成配置

在 Qoder 的 `mcp.json` 中配置：

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

在 Claude Desktop 的 `claude_desktop_config.json` 中配置：

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

> **注意**：MCP 客户端通过 `url` 字段自动识别为 HTTP 模式，无需指定 transport 类型。

### 3. sse 模式

sse (Server-Sent Events) 模式使用服务器发送事件协议，适合服务器向客户端推送实时数据。

```bash
# 使用默认配置启动
weather-mcp --transport sse

# 自定义主机和端口
weather-mcp --transport sse --host 127.0.0.1 --port 3000
```

#### sse 模式集成配置

在 Qoder 的 `mcp.json` 中配置：

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

在 Claude Desktop 的 `claude_desktop_config.json` 中配置：

```json
{
  "mcpServers": {
    "weather": {
      "url": "http://localhost:8080/sse"
    }
  }
}
```

> **注意**：SSE 模式已逐渐被 streamable-http 取代，建议优先使用 `/mcp` 端点。

## 命令行参数

```
usage: weather-mcp [-h] [--transport {stdio,sse,streamable-http}] [--host HOST] [--port PORT]

Weather MCP Server

options:
  -h, --help            显示帮助信息
  --transport {stdio,sse,streamable-http}
                        传输类型：stdio（默认）、sse 或 streamable-http
  --host HOST           HTTP 服务器主机（默认: 0.0.0.0，仅用于 sse/streamable-http 模式）
  --port PORT           HTTP 服务器端口（默认: 8080，仅用于 sse/streamable-http 模式）
```

## 测试方法

### 使用 MCP Inspector（推荐）

MCP Inspector 是一个官方的 Web 可视化测试工具，可以连接 stdio 或 HTTP 模式的 MCP Server 进行交互式测试。

#### 启动 Inspector

```bash
npx @modelcontextprotocol/inspector
```

启动后会自动打开浏览器访问 `http://localhost:6274`，Inspector 内部代理服务运行在 `6277` 端口。

#### 连接配置

**stdio 模式测试：**
- Transport: `stdio`
- Command: `python`
- Arguments: `-m weather_mcp.server`

**streamable-http 模式测试：**
1. 先启动 HTTP 服务器：
   ```bash
   weather-mcp --transport streamable-http --port 8080
   ```
2. 在 Inspector 中选择：
   - Transport: `HTTP`
   - URL: `http://localhost:8080/mcp`

**sse 模式测试：**
1. 先启动 SSE 服务器：
   ```bash
   weather-mcp --transport sse --port 8080
   ```
2. 在 Inspector 中选择：
   - Transport: `HTTP`
   - URL: `http://localhost:8080/sse`

> **注意**：HTTP 模式（streamable-http/sse）需要先在 Inspector 外启动服务器，然后在 Inspector 中填入对应的 URL 地址进行连接。

## 三种模式对比

| 特性 | stdio 模式 | sse 模式 | streamable-http 模式 |
|------|-----------|----------|---------------------|
| 运行方式 | 作为子进程运行 | 作为独立服务器运行 | 作为独立服务器运行 |
| 通信方式 | 标准输入输出 | Server-Sent Events | 流式 HTTP |
| 适用场景 | 本地 AI 助手集成 | 实时数据推送 | 远程服务、微服务架构 |
| 多客户端支持 | 否（单宿主） | 是 | 是 |
| 网络访问 | 仅限本地 | 支持远程访问 | 支持远程访问 |
| 启动速度 | 快 | 稍慢 | 稍慢 |
| 端点路径 | - | `/sse` | `/mcp` |
| Inspector 测试 | 直接启动 | 需先启动服务，URL: `http://host:port/sse` | 需先启动服务，URL: `http://host:port/mcp` |

## 可用工具

### get_current_weather_tool

获取指定城市的当前天气信息。

**参数:**
- `city` (string): 城市名称，如 "Beijing", "London", "New York"

**返回:** 包含温度、湿度、风速、天气状况等信息的字典

### get_weather_forecast_tool

获取指定城市的天气预报。

**参数:**
- `city` (string): 城市名称
- `days` (int): 预报天数（1-7，默认 3）

**返回:** 包含多日预报信息的字典

### list_supported_cities_tool

列出所有支持的城市。

**返回:** 城市列表，包含城市名称、国家和坐标信息

## 技术栈

- Python 3.10+
- MCP Protocol
- FastMCP

## 许可证

MIT
