"""LM Studio（ローカルLLM）を使用するエージェント構成。

カスタムツールとA2A統合機能を備えたローカルLLMエージェント。
A2Aプロトコルを通じて他のエージェント（LangChain等）をオーケストレーションできる。
"""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from common.a2a_tools import ask_translator_agent, list_available_agents
from common.tools import calculate, get_current_time

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
    description="ローカルLLMで動作するAIオーケストレーター",
    tools=[
        get_current_time,
        calculate,
        ask_translator_agent,
        list_available_agents,
    ],
    instruction=(
        "あなたはAIオーケストレーターです。"
        "ユーザーの質問に日本語で丁寧に回答してください。\n\n"
        "利用可能なツール:\n"
        "- get_current_time: 現在時刻の取得\n"
        "- calculate: 数式の計算\n"
        "- ask_translator_agent: 翻訳エージェント（LangChain）に質問\n"
        "- list_available_agents: 利用可能なエージェント一覧\n\n"
        "翻訳に関するリクエストは、ask_translator_agentを使って"
        "翻訳エージェントに委譲してください。"
    ),
)
