import json
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Literal, Any

class ToolCall(BaseModel):
    """
    标准化工具调用请求
    """
    id: str
    function_name: str
    function_args: str  # 原始 JSON 字符串，例如 '{"location": "Beijing"}'
    type: Literal["function"] = "function"

    @computed_field
    @property
    def args_dict(self) -> dict[str, Any]:
        """
        自动将 JSON 字符串转为 Python 字典。
        这样在业务逻辑里直接调 tool_call.args_dict 即可，不用手写 json.loads。
        """
        try:
            return json.loads(self.function_args)
        except json.JSONDecodeError:
            return {}

    model_config = ConfigDict(extra="ignore")

class LLMResponse(BaseModel):
    """
    LLM 的标准化响应（ReAct 的核心判断依据）
    """
    content: str | None = None
    reasoning_content: str | None = None  # 思考链内容 (增量)
    
    # --- 用于后期分析的最终结果 (仅在流式最后一帧或非流式中提供) ---
    final_content: str | None = None
    final_reasoning: str | None = None
    
    tool_calls: list[ToolCall] | None = None
    
    # Token 统计
    usage: dict[str, int] = Field(
        default_factory=lambda: {
            "prompt_tokens": 0, 
            "completion_tokens": 0,
            "reasoning_tokens": 0  # 新增：记录思考消耗的 token
        }
    )
    
    # 停止原因：'stop' | 'tool_calls' | 'length' | 'content_filter'
    finish_reason: Literal["stop", "tool_calls", "length", "content_filter"] | None = None

    model_config = ConfigDict(extra="ignore")
