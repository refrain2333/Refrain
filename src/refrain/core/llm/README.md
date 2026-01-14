# LLM 底座设计理念 (core/llm)

本模块是 **Refrain** 的智能核心，作为统一的模型适配层，负责屏蔽不同 LLM 供应商的协议差异，为上层编排引擎提供标准化、高性能的对话与结构化输出能力。

## 1. 设计核心：策略模式 (Strategy Pattern)
- **BaseLLM (base.py)**: 纯粹的生成模型接口。负责 `chat`、`stream_chat` 和 `structured_chat`，驱动 Agent 的思考与对话。
- **BaseEmbedder (vector/base.py)**: 纯粹的向量接口。负责将文本转换为高维向量，是 RAG (检索增强生成) 的语义基础。
- **OpenAIProvider (openai_provider.py)**: 目前工业界事实上的标准实现。

## 2. 为什么拆分 Chat 和 Vector？
1. **职责分离**: 生成（Generation）和表示（Representation）是两种完全不同的模型能力。
2. **组合灵活性**: 支持“云端大脑 + 本地记忆”的混搭模式。例如：使用 GPT-4o 作为 Chat 模型（聪明），使用本地 BGE 模型作为 Vector 模型（隐私、免费）。

## 2. 数据标准：双轨制响应 (Dual-Track Response)
在 `schemas.py` 中，我们将响应定义为：
- **增量轨道**: 用于前端实时渲染的 `content` 和 `reasoning_content`。
- **终局轨道**: 用于后台逻辑分析的 `final_content` 和 `final_reasoning`（确保流式结束后能拿到全量文本）。

## 3. 未来扩展轨道 (TODO)
为了将 Refrain 打造为完整的 AI 代码助手，底座预留了以下扩展方向：
- **Embed (向量)**: RAG 语义搜索的核心，用于在大规模代码库中精准定位。
- **Complete (补全)**: 基于 FIM (Fill-In-the-Middle) 模式，实现类似 Copilot 的行内代码补全。

## 4. 待办任务清单 (Roadmap)
### 近期任务 (Near-term)
- [ ] **流式结构化输出 (Fourth Track)**: 实现 `stream_structured_chat`，支持在 UI 上实时展示 Pydantic 对象。需要调研 `partial-json-parser` 或 `Instructor` 的集成。
- [ ] **LiteLLM 适配器**: 增加 `LiteLLMProvider`，使 Refrain 能够通过统一接口调用 Anthropic、Google Gemini 及各类本地模型。
- [ ] **配置系统联调**: 将 `factory.py` 与 `core/config/settings` 完整对接，实现从配置文件加载模型凭证。

## 5. 核心哲学
1. **ReAct 驱动**: 所有的响应都必须包含 `finish_reason` 和 `tool_calls` 状态，这是驱动编排层进行思考循环的关键信号。
2. **极致健壮**: 自动处理不同平台对思考链（reasoning）的不同返回方式（有的在字段里，有的在正文里）。
3. **依赖注入 (factory.py)**: 使用单例缓存（LRU Cache），既支持全局默认模型，也支持在调用时动态注入特定的 API Key 或模型 ID（支持“接私活”模式）。

## 4. 关键原则
- **底座不带业务**: 这一层只管“说话”和“传输”，不涉及任何业务逻辑。
- **异步优先**: 全链路支持 `async/await`，适配高性能并发场景。

