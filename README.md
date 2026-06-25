# PathBook · 小路书

> AI-driven personalized route planning assistant
> AI 驱动的个性化路线规划助手

[English](#english) | [中文](#中文)

---

<a id="english"></a>

## English

### Overview

**PathBook (小路书)** is an AI-driven personalized route planning assistant. It transforms ambiguous user queries (e.g. *"I want a chill weekend in Shanghai with good coffee and no crowds"*) into structured, time-aware, and reality-checked itineraries.

The system covers the full pipeline from intent understanding, candidate generation, route composition, real-time POI verification, to user profile learning — delivered to the client as a progressively streamed (SSE) experience.

### Project Status

| Item | Value |
|------|-------|
| Stage | **MVP** |
| Backend | Python · FastAPI · MySQL |
| Client | iOS · SwiftUI (MVPM) |
| Architecture | 6 high-level domains |

### Architecture (Level-1 Domains)

The system is organized into six domains. The first-level architecture deliberately stays coarse-grained — only when the boundaries between domains are agreed upon will each domain owner drill down into level-2 modules and interface contracts.

| # | Domain | Responsibility | Out of Scope |
|---|--------|----------------|--------------|
| ① | **Gateway** | Auth · rate limiting · routing · SSE | No business orchestration |
| ② | **Understanding & Slot Filling** | Turn fuzzy query + context into a structured, complete request | No candidate generation |
| ③ | **Route Engine** | Candidate generation → composition into a timeline route | No verification, no profiling |
| ④ | **Verification** | Real-time POI status confirmation (AI / human / fallback) | No routing decisions |
| ⑤ | **Profile & Behavior** | User preferences, behavior stream, historical routes | Not on the realtime hot path |
| ⑥ | **Infrastructure** | Unified LLM access · external data adapters (Amap / Baidu / Dianping ...) | No business logic |

#### Real-time main flow

```
User → Gateway → Understanding → Route Engine → Verification → Route Engine → Gateway → User (SSE)
```

#### Side flows

- **Profile (dashed)**: read by *Understanding* and *Route Engine*; written asynchronously via *Gateway* — never blocks the main path.
- **Infrastructure (dashed)**: shared by *Understanding*, *Route Engine* and *Verification*; isolates vendor differences for LLMs and data sources.

For the full diagram and rationale see [`backend/docs/architecture-l1-domains.md`](docs/architecture-l1-domains.md).

### Repository Layout

```
PathBook/
├── .codebuddy/
│   └── rules/
│       └── project-rules.md              # AI-assisted development rules (always applied)
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI entry point (/health)
│   │   ├── config.py                     # pydantic-settings config
│   │   ├── gateway/                      # ① Gateway: routing & orchestration
│   │   │   ├── router.py
│   │   │   ├── orchestrator.py
│   │   │   └── schemas.py
│   │   ├── understanding/                # ② Understanding & Slot Filling
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── route_engine/                 # ③ Route Engine
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── verification/                 # ④ Verification
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── profile/                      # ⑤ Profile & Behavior
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── infra/                        # ⑥ Infrastructure
│   │   │   ├── database.py
│   │   │   ├── llm/
│   │   │   ├── external/
│   │   │   └── toolkit/
│   │   └── shared/                       # Cross-domain shared (exceptions, response)
│   │       ├── exceptions.py
│   │       └── response.py
│   ├── tests/
│   ├── pyproject.toml
│   ├── .env.example
│   └── .gitignore
├── docs/
│   ├── architecture-l1-domains.md
│   └── project-rules.md                  # Detailed engineering specification
└── frontend/                             # iOS SwiftUI client (planned)
```

### Quick Start

**Requirements**: Python ≥ 3.9, MySQL 8.x (for running server; tests use SQLite in-memory)

```bash
cd backend

# 1. Create virtual environment & install dependencies (uv recommended)
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Or with standard pip:
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. Configure environment variables
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET and DATABASE_URL

# 3. Start dev server (default port: 8000)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

After startup:
- Health check: http://localhost:8000/health
- API docs (Swagger): http://localhost:8000/docs
- Ping: http://localhost:8000/api/v1/ping

#### Run Tests (no MySQL needed)

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### Engineering Conventions

- **Python ≥ 3.9 compatibility** — type annotations must use `typing` module constructs (`Optional[X]`, `List[str]`, `Dict[str, Any]`) instead of Python 3.10+ syntax (`X | Y`, `list[str]`). This ensures runtime compatibility with Python 3.9+.
- **Domain isolation** — domains communicate via interfaces; no cross-domain access to internal implementation.
- **LLM access centralized** — all LLM calls go through the Infrastructure domain. Business code must not `import openai` directly.
- **Secrets via environment only** — managed by `python-dotenv` / `.env`; never committed.
- **Strict validation** — inputs validated by Pydantic; outputs follow `{ code, data, message }`.
- **Type hints required** — no untyped function signatures.
- **Small commits** — `feat(scope): description`.

### AI-Assisted Development Workflow

Each feature follows a five-phase loop with a corresponding skill triggered at each checkpoint:

| Phase | Skill | Deliverable |
|-------|-------|-------------|
| 1. Requirement | `brainstorming` | Clear input / output / boundaries / non-goals |
| 2. Design | `writing-plans` | Step-by-step plan with dependencies & acceptance criteria |
| 3. Implementation | `test-driven-development` | One module at a time, no cross-domain leaks |
| 4. Verification | `verification-before-completion` | "Done" requires green runs |
| 5. Debugging | `systematic-debugging` | Reproduce → locate → fix; never guess |

### Documentation Index

| Document | Path |
|----------|------|
| Level-1 Architecture | [`backend/docs/architecture-l1-domains.md`](docs/architecture-l1-domains.md) |
| Project Rules | [`backend/docs/project-rules.md`](docs/project-rules.md) |
| MVP Task List | *TBD* |
| Interface Contracts | *TBD* |

### License

To be determined.

---

<a id="中文"></a>

## 中文

### 项目简介

**小路书 (PathBook)** 是一款 AI 驱动的个性化路线规划助手。它能把用户模糊的自然语言诉求（例如 *"周末在上海，找点好咖啡，别太挤"*）转化为结构化、有时间轴、并经过实时核验的可执行路线。

系统覆盖从意图理解、候选生成、路线串接、POI 实时核验到用户画像沉淀的完整链路，并以流式（SSE）方式渐进式返回给客户端。

### 项目状态

| 项目 | 内容 |
|------|------|
| 阶段 | **MVP** |
| 服务端 | Python · FastAPI · MySQL |
| 客户端 | iOS · SwiftUI（MVVM） |
| 架构 | 6 大域 |

### 一级架构（域划分）

系统按职责划分为 6 个大域。第一阶段刻意保持粗粒度，只有在大域边界达成共识后，各域 Owner 才会向下拆分二级模块与接口契约。

| 序号 | 大域 | 职责（一句话） | 不做什么 |
|------|------|----------------|----------|
| ① | **接入层** | 鉴权 · 限流 · 路由 · SSE | 不做业务编排 |
| ② | **理解与补齐域** | 把模糊 Query + 上下文变成结构化的完整需求 | 不出候选 |
| ③ | **路线引擎域** | 候选生成 → 串接成时间轴路线 | 不做核验、不算画像 |
| ④ | **核验体系域** | 对关键 POI 做实时状态确认（AI / 真人 / 降级） | 不做路线决策 |
| ⑤ | **画像与行为域** | 偏好沉淀、行为流、历史路线 | 不参与实时主链路 |
| ⑥ | **基础设施域** | 统一 LLM 接入与外部数据适配（高德 / 百度 / 点评等） | 不做业务判断 |

#### 实时主链路

```
用户 → 接入层 → 理解补齐 → 路线引擎 → 核验 → 路线引擎 → 接入层 → 用户（SSE）
```

#### 旁路

- **画像旁路（虚线）**：理解补齐域、路线引擎域**读**画像；用户行为通过接入层**异步写入**，不阻塞主流程。
- **基础设施旁路（虚线）**：理解、引擎、核验复用 LLM 与数据适配，所有外部依赖统一收敛，便于替换、灰度、限流、降级。

完整架构图与设计取舍见 [`backend/docs/architecture-l1-domains.md`](docs/architecture-l1-domains.md)。

### 仓库结构

```
PathBook/
├── .codebuddy/
│   └── rules/
│       └── project-rules.md              # AI 辅助开发规则（始终生效）
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI 入口（/health）
│   │   ├── config.py                     # pydantic-settings 配置
│   │   ├── gateway/                      # ① 接入层：路由与编排
│   │   │   ├── router.py
│   │   │   ├── orchestrator.py
│   │   │   └── schemas.py
│   │   ├── understanding/                # ② 理解与补齐域
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── route_engine/                 # ③ 路线引擎域
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── verification/                 # ④ 核验体系域
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── profile/                      # ⑤ 画像与行为域
│   │   │   ├── service.py
│   │   │   └── schemas.py
│   │   ├── infra/                        # ⑥ 基础设施域
│   │   │   ├── database.py
│   │   │   ├── llm/
│   │   │   ├── external/
│   │   │   └── toolkit/
│   │   └── shared/                       # 跨域共享（异常、响应格式）
│   │       ├── exceptions.py
│   │       └── response.py
│   ├── tests/
│   ├── pyproject.toml
│   ├── .env.example
│   └── .gitignore
├── docs/
│   ├── architecture-l1-domains.md
│   └── project-rules.md                  # 工程规范详版
└── frontend/                             # iOS SwiftUI 客户端（规划中）
```

### 快速启动

**前置要求**：Python ≥ 3.9，MySQL 8.x（运行服务器需要；跑测试使用 SQLite 内存库，无需 MySQL）

```bash
cd backend

# 1. 创建虚拟环境并安装依赖（推荐用 uv）
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# 或者用标准 pip：
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，至少设置 JWT_SECRET 和 DATABASE_URL

# 3. 启动开发服务器（默认端口：8000）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后可访问：
- 健康检查：http://localhost:8000/health
- API 文档（Swagger）：http://localhost:8000/docs
- Ping：http://localhost:8000/api/v1/ping

#### 运行测试（无需 MySQL）

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

### 工程约束

- **Python ≥ 3.9 兼容**：类型注解必须使用 `typing` 模块写法（`Optional[X]`、`List[str]`、`Dict[str, Any]`），禁止使用 Python 3.10+ 的 `X | Y` 联合语法和内置泛型下标 `list[str]`。确保运行时兼容 Python 3.9+。
- **域间隔离**：域之间通过接口通信，不跨域引用内部实现。
- **LLM 调用收敛**：所有 LLM 调用走基础设施域，业务层不直接 `import openai`。
- **Secret 仅环境变量**：通过 `python-dotenv` / `.env` 管理，禁止入库。
- **严格校验**：输入用 Pydantic 校验，输出统一 `{ code, data, message }`。
- **类型提示必写**：禁止无类型函数签名。
- **小步 commit**：`feat(scope): description`。

### AI 辅助开发流程

每个功能按五阶段闭环推进，每个关键节点加载对应 Skill：

| 阶段 | Skill | 产出 |
|------|-------|------|
| 1. 需求明确 | `brainstorming` | 明确的输入 / 输出 / 边界 / 不做什么 |
| 2. 方案设计 | `writing-plans` | 含依赖、顺序、验收标准的分步计划 |
| 3. 编码实现 | `test-driven-development` | 每次只做一个模块，域间不互相穿透 |
| 4. 验证完成 | `verification-before-completion` | 必须跑通才能说"完成" |
| 5. Bug 修复 | `systematic-debugging` | 先复现、再定位、再修复，不猜 |

### 文档索引

| 文档 | 路径 |
|------|------|
| 一级架构 | [`backend/docs/architecture-l1-domains.md`](docs/architecture-l1-domains.md) |
| 项目规范 | [`backend/docs/project-rules.md`](docs/project-rules.md) |
| MVP 任务列表 | *待补充* |
| 接口契约 | *待补充* |

### 许可证

待定。
