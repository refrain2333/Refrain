from typing import AsyncGenerator, override, Any, Type, TypeVar
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel

from core.config import settings
from .base import BaseLLM
from .schemas import LLMResponse, ToolCall

T = TypeVar("T", bound=BaseModel)

class OpenAIProvider(BaseLLM):
    def __init__(
        self, 
        api_key: str | None = None, 
        base_url: str | None = None, 
        default_model: str | None = None
    ):
        self.client = AsyncOpenAI(
            api_key=api_key or settings.OPENAI_API_KEY,
            base_url=base_url or settings.OPENAI_API_BASE,
        )
        self.default_model = default_model or settings.DEFAULT_LLM_MODEL

    def _parse_response(self, response: ChatCompletion) -> LLMResponse:
        choice = response.choices[0]
        message = choice.message
        
        normalized_tools = []
        if message.tool_calls:
            for tc in message.tool_calls:
                normalized_tools.append(ToolCall(
                    id=tc.id,
                    function_name=tc.function.name,
                    function_args=tc.function.arguments
                ))

        # 智能提取 Token 消耗（适配 OpenAI 最新推理模型标准）
        usage = response.usage
        reasoning_tokens = 0
        if usage:
            # 安全获取 details 对象，确保它不是 None 再取值 (解决潜在的 NoneType 报错)
            details = getattr(usage, "completion_tokens_details", None)
            if details:
                reasoning_tokens = getattr(details, "reasoning_tokens", 0)

        usage_dict = {
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "reasoning_tokens": reasoning_tokens
        }

        # 极致兼容的思考链抓取 (适配 DeepSeek-R1)
        reasoning = getattr(message, "reasoning_content", None)

        return LLMResponse(
            content=message.content,
            final_content=message.content,  # 非流式模式，定稿等于当前内容
            reasoning_content=reasoning,
            final_reasoning=reasoning,     # 非流式模式，定稿等于当前内容
            tool_calls=normalized_tools if normalized_tools else None,
            usage=usage_dict,
            finish_reason=choice.finish_reason # type: ignore
        )

    def _convert_tool_buffer(self, buffer: dict) -> list[ToolCall] | None:
        """内部助手：将缓存的碎片转为标准的 ToolCall 对象列表"""
        if not buffer:
            return None
        return [
            ToolCall(
                id=v["id"] or "", 
                function_name=v["name"], 
                function_args=v["args"]
            ) for v in buffer.values()
        ]

    @override
    async def chat(
        self, 
        messages: list[dict[str, Any]], 
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict = "auto",
        **kwargs
    ) -> LLMResponse:
        api_kwargs = {"messages": messages, "model": kwargs.pop("model", self.default_model), **kwargs}
        if tools:
            api_kwargs["tools"] = tools
            api_kwargs["tool_choice"] = tool_choice

        response = await self.client.chat.completions.create(**api_kwargs)
        return self._parse_response(response)

    @override
    async def structured_chat(
        self, 
        messages: list[dict[str, Any]], 
        response_model: Type[T],
        **kwargs
    ) -> T:
        """使用 OpenAI Beta 的 parse 接口实现极高成功率的结构化输出"""
        completion = await self.client.beta.chat.completions.parse(
            model=kwargs.pop("model", self.default_model),
            messages=messages,
            response_format=response_model,
            **kwargs
        )
        return completion.choices[0].message.parsed # type: ignore

    @override
    async def stream_chat(
        self, 
        messages: list[dict[str, Any]], 
        **kwargs
    ) -> AsyncGenerator[LLMResponse, None]:
        # 在流式中开启 stream_options 以获取 token 消耗统计
        stream_kwargs = {
            "model": kwargs.pop("model", self.default_model),
            "messages": messages,
            "stream": True,
            "stream_options": {"include_usage": True}, # 必须开启此项才能在流式中拿到 usage
            **kwargs
        }
        
        stream = await self.client.chat.completions.create(**stream_kwargs)
        
        # 状态累加器
        full_content = ""
        full_reasoning = ""
        full_usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}
        tool_calls_buffer: dict[int, dict[str, Any]] = {}
        last_finish_reason = None
        has_yielded_final = False

        async for chunk in stream:
            # 1. 处理 Usage 帧 (通常是最后一帧)
            if not chunk.choices:
                if chunk.usage:
                    u = chunk.usage
                    full_usage["prompt_tokens"] = u.prompt_tokens
                    full_usage["completion_tokens"] = u.completion_tokens
                    details = getattr(u, "completion_tokens_details", None)
                    if details:
                        full_usage["reasoning_tokens"] = getattr(details, "reasoning_tokens", 0)
                
                # 标记已产出最终帧
                has_yielded_final = True
                yield LLMResponse(
                    content=None,
                    reasoning_content=None,
                    final_content=full_content,
                    final_reasoning=full_reasoning if full_reasoning else None,
                    tool_calls=self._convert_tool_buffer(tool_calls_buffer),
                    usage=full_usage,
                    finish_reason=last_finish_reason or "stop"
                )
                continue

            choice = chunk.choices[0]
            delta = choice.delta
            last_finish_reason = choice.finish_reason
            
            # 2. 累加内容并记录增量
            delta_content = delta.content
            if delta_content:
                full_content += delta_content
            
            delta_reasoning = getattr(delta, "reasoning_content", None)
            if delta_reasoning:
                full_reasoning += delta_reasoning

            # 3. 累加工具调用碎片
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_buffer:
                        tool_calls_buffer[idx] = {"id": tc.id, "name": "", "args": ""}
                    if tc.id: 
                        tool_calls_buffer[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls_buffer[idx]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_calls_buffer[idx]["args"] += tc.function.arguments

            # 4. 实时产出增量响应 (包含当前的完整 tool_calls 状态)
            yield LLMResponse(
                content=delta_content,
                reasoning_content=delta_reasoning,
                tool_calls=self._convert_tool_buffer(tool_calls_buffer),
                finish_reason=choice.finish_reason # type: ignore
            )

        # --- 兜底逻辑：如果循环结束了还没产出过 final 帧 (有些平台最后一帧不带 usage) ---
        if not has_yielded_final:
            yield LLMResponse(
                content=None,
                reasoning_content=None,
                final_content=full_content,
                final_reasoning=full_reasoning if full_reasoning else None,
                tool_calls=self._convert_tool_buffer(tool_calls_buffer),
                usage=full_usage,
                finish_reason=last_finish_reason or "stop"
            )
