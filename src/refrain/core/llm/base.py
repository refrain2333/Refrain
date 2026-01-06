from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar, AsyncGenerator
from pydantic import BaseModel
from .schemas import LLMResponse

# 定义泛型，用于结构化输出的类型推导
T = TypeVar("T", bound=BaseModel)

class BaseLLM(ABC):
    """
    对话模型基类 (支持双轨制：自由对话 + 结构化任务)
    """
    @abstractmethod
    async def chat(
        self, 
        messages: list[dict[str, Any]], 
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str | dict = "auto",
        **kwargs
    ) -> LLMResponse:
        """
        轨道 1：自由对话 (主力)
        适用于：闲聊、写文章、解释概念、情感陪伴。
        """
        pass

    @abstractmethod
    async def structured_chat(
        self, 
        messages: list[dict[str, Any]], 
        response_model: Type[T],
        **kwargs
    ) -> T:
        """
        轨道 2：结构化任务 (特种兵)
        适用于：意图识别、提取关键词、评分、数据库字段生成。
        返回：指定的 Pydantic 对象
        """
        pass

    @abstractmethod
    async def stream_chat(
        self, 
        messages: list[dict[str, Any]], 
        **kwargs
    ) -> AsyncGenerator[LLMResponse, None]:
        """
        轨道 3：流式输出 (前端展示)
        适用于：打字机效果的实时聊天。
        返回：包含增量内容或元数据的 LLMResponse 块
        """
        pass
