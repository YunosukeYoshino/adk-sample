"""Gemini APIを使用するbasicエージェントパッケージ。

Google ADKとGeminiモデルを使用した日本語AIアシスタント。
"""

from .agent import root_agent

__all__ = ["root_agent"]
