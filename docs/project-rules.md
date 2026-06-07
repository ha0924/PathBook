# 小路书 · Project Rules

> AI 辅助开发规范。所有开发活动遵循此文件。

---

## 项目信息

- **项目**：小路书 — AI 驱动的个性化路线规划助手
- **阶段**：MVP
- **服务端**：Python + FastAPI + MySQL
- **客户端**：iOS SwiftUI (MVVM)
- **架构**：6 大域（接入层 / 理解补齐 / 路线引擎 / 核验 / 画像行为 / 基础设施）

---

## 开发流程 & Skills 触发

每个功能/模块按以下流程推进，关键节点加载对应 skill：

```text
1. 需求明确
   └─ 触发 skill: brainstorming
   └─ 产出：明确的输入/输出/边界/不做什么

2. 方案设计
   └─ 触发 skill: writing-plans
   └─ 产出：分步实现计划（含依赖、顺序、验收标准）

3. 编码实现
   └─ 触发 skill: test-driven-development（如需要）
   └─ 规则：每次只做一个模块，域间不直接引用内部实现

4. 验证完成
   └─ 触发 skill: verification-before-completion
   └─ 规则：必须跑通才能说"完成"

5. 遇到 Bug
   └─ 触发 skill: systematic-debugging
   └─ 规则：先复现、再定位、再修复，不猜
```

---

## 基本约束

- 域间通过接口通信，不跨域引用内部实现
- LLM 调用走基础设施域，业务层不直接 `import openai`
- Secret 只从环境变量读取（python-dotenv / .env）
- 输入用 Pydantic 校验，输出统一 `{ code, data, message }`
- 类型提示必须写，禁止无类型函数签名
- 小步 commit：`feat(scope): description`

---

## 文档索引

| 文档 | 路径 |
|------|------|
| 一级架构 | `docs/architecture-l1-domains.md` |
| 项目规范 | `docs/project-rules.md`（本文件） |
| MVP 任务列表 | TBD |
| 接口契约 | TBD |
