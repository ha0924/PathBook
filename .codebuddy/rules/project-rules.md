---
description: 小路书项目核心规范，所有开发活动必须遵循
alwaysApply: true
---

# 小路书项目规范（入口）

本项目所有 AI 辅助开发活动必须遵循 `docs/project-rules.md` 中定义的规范。

## 项目快速上下文

- **项目**：小路书 — AI 驱动的个性化路线规划助手
- **阶段**：MVP
- **服务端**：Python + FastAPI + MySQL
- **客户端**：iOS SwiftUI (MVVM)
- **架构**：6 大域 — 接入层 / 理解补齐 / 路线引擎 / 核验 / 画像行为 / 基础设施

## 核心原则

1. **域间通过接口契约通信**，不跨域引用内部实现
2. **LLM 调用走基础设施域**，业务层不直接 import LLM SDK
3. **Secret 只从环境变量读取**，禁止硬编码
4. **类型提示必须写**，输入用 Pydantic 校验
5. **小步 commit**，格式：`feat(scope): description`

## 开发流程（关键节点触发 superpowers skill）

| 阶段 | 触发 skill |
|------|-----------|
| 需求明确 | `brainstorming` |
| 方案设计 | `writing-plans` |
| 编码实现（视情况） | `test-driven-development` |
| 验证完成 | `verification-before-completion` |
| 调试 Bug | `systematic-debugging` |

## 完整规范

详细规则、文档索引、约束细则见：`docs/project-rules.md`

在开始任何开发任务前，请先阅读该文档。
