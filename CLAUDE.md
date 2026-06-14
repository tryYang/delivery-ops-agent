# Delivery Ops Agent — Claude 项目规范

本文件与 [`.cursor/rules/project-standards.mdc`](.cursor/rules/project-standards.mdc) 对齐。在本仓库编码时始终遵守。

领域专项规则见 `.claude/skills/` 与 `docs/agent-skills/`（架构、工单、验收）。

## 注释

- 在关键业务边界、非显然设计决策、状态转换、IO/外部系统交互处写**有用**注释。
- 注释说明 **why**，不重复代码 **what**。
- 禁止为显而易见的一两行代码写注释。

```python
# ✅ 说明边界或约束
# unknown 意图不创建任务，避免污染 TaskStore。
if intent == TaskIntent.UNKNOWN:
    return self._report_publisher.build_unknown(intent)

# ❌ 无信息增量
# 调用 classify 方法
intent = self._intent_router.classify(message.text)
```

## 架构

- 依赖方向：`domain` → `application` → `graphs` / `adapters` / `storage`。
- `domain/` 不依赖 FastAPI、LangGraph、SDK、ORM；平台 payload 在 adapter 层转为领域模型。
- Bug Fix 与 Feature Development 独立 Graph、状态、证据、工单、风险、验收。
- 可共享：adapters、storage、executors、reporting、audit。
- 入口统一为 `IngressPort`；执行器只执行，Quality Gate 独立验收。

## Python

- Pydantic v2、`typing.Protocol` 端口、显式类型，避免 `Any`。
- 文件顶部使用 `from __future__ import annotations`。
- async IO 需 try/except 与空值处理。
- 构造函数注入依赖；函数保持短小（< 30 行为宜）。
- ID：`uuid4`；时间戳：`datetime.now(UTC)`。

## 测试

- 新增或修改行为需配套单元或集成测试。
- 测试目录镜像 `src/`；核心链路变更后运行 `pytest -v`。

## 变更约束

- 不主动新增 README、示例文档、ChangeLog（用户明确要求除外）。
- 不修改 `.cursor/plans/` 计划文件；不提前引入当前 Phase 外的 FastAPI、Hermes、LangGraph runtime、执行器、Quality Gate。
