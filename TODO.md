# TODO

## 增加身份认证

当前 MCP Server 在 HTTP 模式（SSE / Streamable HTTP）下没有身份认证机制，任何人都可以直接访问。需要增加认证以保护服务。

### 方案选择

#### 方案一：API Key / Bearer Token（推荐用于内部使用）

- 通过 Starlette 中间件拦截请求，校验 `Authorization: Bearer <key>` 头
- 简单易实现，适合内部团队或开发环境
- 需配合 HTTPS 使用，防止 key 泄露

#### 方案二：OAuth 2.1（推荐用于公网暴露）

- MCP 协议规范（2024-11-05）定义的标准认证流程
- Server 暴露 `/.well-known/oauth-authorization-server` 元数据
- Client 通过标准 OAuth 流程获取 access token
- `mcp` Python SDK 已内置支持

#### 方案三：反向代理层认证

- 不修改 MCP Server 代码，在前面加 Nginx / Traefik 等反向代理
- 由代理层负责认证（API Key、JWT、mTLS 等）
- 适合已有网关基础设施的场景

### 适用场景

| 场景 | 推荐方案 |
|------|---------|
| 本地/开发使用 | 无需认证（stdio 模式） |
| 内部团队使用 | 方案一：API Key + HTTPS |
| 公网暴露 | 方案二：OAuth 2.1 |
| 已有网关/基础设施 | 方案三：反向代理层认证 |
