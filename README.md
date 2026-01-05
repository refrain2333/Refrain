# Refrain

基于 Python 的 AI 代码助手 — **迭代精进，适度克制**

透明的 Diff 展示 + 用户确认的每一步代码修改。从不黑盒化处理。

> *"Every great code change is a refrain — iterative, refined, restrained."*  
> *每一次伟大的代码变更都是一段「副歌」—— 往复打磨，精致且克制。*

**Refrain** 的双重灵魂：
- **副歌（Noun）** — 代码需要反复打磨，像音乐中被反复吟唱的部分
- **克制（Verb）** — AI 被关在安全笼子里，拒绝不可控的修改

## 核心价值观

-  **[ITERATE] 往复打磨** - 每次编辑都是一次「副歌」的打磨
-  **[RESTRAIN] 克制有度** - Diff 透明 → 用户确认 → 才修改

### 设计原则

- 慢即是快 — 专注原子化修改，把每件事做到完美
- 透明至上 — Diff 是唯一的真理，任何修改前必须用户确认
- 人机协奏 — 人类是指挥家，AI 提供旋律


## 项目架构

```
src/refrain/
├── cli/              # 1. CLI 交互层
├── engine/           # 2. 编排执行层（ReAct 循环）
├── skills/           # 3. 工具系统层
├── core/             # 4. 核心基建层（LLM、配置）
├── utils/            # 5. 辅助工具层
└── resources/        # 6. 资源层（提示词）
```
