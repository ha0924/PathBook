# Infrastructure Foundation

> 项目基础设施四大件：日志、异常、响应格式、i18n。所有业务模块基于此开发。

---

## 概览

| 模块 | 职责 | 位置 |
|------|------|------|
| 日志 | 结构化 JSON 日志，请求追踪 | `shared/logger.py` |
| 异常 | 统一异常基类 + 错误码枚举 | `shared/exceptions.py` |
| 响应 | 统一 JSON 响应结构 | `shared/response.py` |
| i18n | 多语言错误消息 | `shared/i18n.py` + `shared/locales/` |
| 衔接 | 全局异常处理器 | `gateway/error_handler.py` |
| 中间件 | request_id + 请求耗时 | `gateway/middleware.py` |
| 安全工具 | 密码哈希 + JWT | `infra/toolkit/security.py` |

---

## 一、日志

- 基于 Python 标准库 `logging`，不引第三方包
- JSON 结构化输出到 stdout（容器友好）
- 每个请求分配 `request_id`，贯穿链路
- 业务模块通过 `get_logger(__name__)` 获取 logger
- 级别由环境变量 `LOG_LEVEL` 控制

---

## 二、异常处理

- 业务层只抛 `BizError(ErrorCode.XXX)`
- 全局处理器统一捕获，自动完成：翻译 message → 推导 HTTP status → 记录日志 → 格式化响应
- 业务代码不关心 HTTP 状态码和消息文本

### 错误码分段

| 段 | 域 | HTTP Status |
|----|----|-------------|
| 10xxx | 通用（未知、参数校验） | 500 / 422 |
| 400xx | 用户/业务错误 | 400 |
| 401xx | 认证（token 过期/无效） | 401 |
| 403xx | 权限 | 403 |
| 500xx | 路线域（预留） | 400 |

---

## 三、统一响应格式

所有接口返回：

```json
{
  "code": 0,
  "data": {},
  "message": "success"
}
```

| 字段 | 说明 |
|------|------|
| code | 0=成功，非0=错误码 |
| data | 成功时为数据，失败时为 null |
| message | 面向用户的消息（走 i18n） |

---

## 四、i18n

- 使用 `python-i18n` 包
- 翻译文件：`shared/locales/{namespace}.{locale}.json`
- 默认 zh_CN，回退 en_US
- 语言检测：请求头 `Accept-Language`
- 启用内存缓存（memoization）
- 业务层统一调用 `t("errors.{code}")` 获取翻译文本
- **所有面向用户的错误消息必须走 i18n，禁止硬编码字符串**

---

## 五、请求中间件

- 注入 `request_id`（UUID4），响应头返回 `X-Request-ID`
- 记录请求方法 + 路径 + 状态码 + 耗时
- 解析 `Accept-Language` 存入 `request.state.locale`

---

## 六、安全工具

- 密码哈希：bcrypt（passlib）
- JWT：HS256 签名，payload 含 `user_id` + `username` + `exp`
- 密钥从环境变量 `JWT_SECRET` 读取，禁止硬编码
- 默认 7 天过期，由 `JWT_EXPIRE_HOURS` 配置

---

## 七、新增依赖

| 包 | 用途 |
|----|------|
| `python-i18n` | 多语言翻译 |
| `passlib[bcrypt]` | 密码哈希 |
| `python-jose[cryptography]` | JWT 签发/验证 |

---

## 八、新增配置项

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JWT_SECRET` | JWT 签名密钥 | 必须修改 |
| `JWT_EXPIRE_HOURS` | Token 过期时间（小时） | 168 |
| `LOG_LEVEL` | 日志级别 | INFO |

---

## 九、规范约束

1. 所有面向用户的错误消息**必须走 i18n**，禁止硬编码字符串
2. 业务层**只抛 BizError**，不直接构造 HTTP 响应
3. 新增错误码必须同步更新两份 locale JSON 文件
4. 密钥、token 等敏感信息只从环境变量读取
5. 业务日志使用 `get_logger(__name__)` 获取，不直接 `print`
