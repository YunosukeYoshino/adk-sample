"""LM Studio（ローカルLLM）を使用するシンプルなエージェント構成."""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# 環境変数から設定を読み込み（デフォルト値あり）
LM_STUDIO_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "openai/google/gemma-3n-e4b")

root_agent = Agent(
    name="local_assistant",
    model=LiteLlm(
        model=LOCAL_LLM_MODEL,
        api_base=LM_STUDIO_BASE,
        api_key=LM_STUDIO_API_KEY,
    ),
    description="ローカルLLMで動作する汎用AIアシスタント",
    instruction="あなたは親切で有能なAIアシスタントです。ユーザーの質問に日本語で丁寧に回答してください。",
)
