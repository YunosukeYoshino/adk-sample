"""LangChainエージェントパッケージ。

LangChain 1.0+とA2Aプロトコルを使用した翻訳エージェント。
"""

from .agent import get_agent, invoke_agent

__all__ = ["get_agent", "invoke_agent"]
