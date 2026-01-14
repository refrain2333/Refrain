from abc import ABC, abstractmethod
from typing import Any, Sequence, TypeVar, Generic

# 定义泛型
T = TypeVar("T")

class BaseEmbedder(ABC):
    """
    轨道 1：向量模型基类 (Model Layer)
    职责：纯粹的“算法”层，负责将文本转换为高维向量空间中的坐标。
    """
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """将单段文本转换为向量（用于查询）"""
        pass

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量转换文档向量（用于索引优化）"""
        pass


class BaseVectorStore(ABC):
    """
    轨道 2：向量检索基类 (Storage/Search Layer)
    职责：纯粹的“工程”层，负责向量的存储、索引构建和高效相似度检索。
    """
    @abstractmethod
    async def add_texts(
        self, 
        texts: Sequence[str], 
        metadatas: list[dict] | None = None,
        **kwargs: Any
    ) -> list[str]:
        """将文本及其元数据持久化到索引中，返回唯一标识符列表"""
        pass

    @abstractmethod
    async def similarity_search(
        self, 
        query_vector: list[float], 
        k: int = 4, 
        **kwargs: Any
    ) -> list[dict]:
        """
        根据向量坐标进行 Top-K 检索。
        返回：包含文本、元数据和相似度评分的结果。
        """
        pass

    @abstractmethod
    async def delete(self, ids: list[str]) -> bool:
        """从存储中移除指定的索引记录"""
        pass
