from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class AIService(ABC):
    @abstractmethod
    async def explain_diary(self, context: dict[str,Any], question: str, language: str) -> str | None:
        raise NotImplementedError
