"""LangChainエージェント定義。

LangChain 1.0+を使用した翻訳エージェントの実装。
"""

import os
from datetime import datetime
from typing import Any

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

# 環境変数から設定を取得（LM Studio対応）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "not-needed")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")


@tool
def get_current_time() -> str:
    """現在時刻を取得する。

    Returns:
        日本語フォーマットの現在時刻文字列。
    """
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H時%M分%S秒")


@tool
def translate_to_english(text: str) -> str:
    """日本語を英語に翻訳する。

    Args:
        text: 翻訳する日本語テキスト。

    Returns:
        英語に翻訳されたテキスト。
    """
    # 簡易的な翻訳辞書（デモ用）
    translations = {
        "こんにちは": "Hello",
        "ありがとう": "Thank you",
        "さようなら": "Goodbye",
    }
    return translations.get(text, f"[Translation of: {text}]")


@tool
def translate_to_japanese(text: str) -> str:
    """英語を日本語に翻訳する。

    Args:
        text: 翻訳する英語テキスト。

    Returns:
        日本語に翻訳されたテキスト。
    """
    # 簡易的な翻訳辞書（デモ用）
    translations = {
        "Hello": "こんにちは",
        "Thank you": "ありがとう",
        "Goodbye": "さようなら",
    }
    return translations.get(text, f"[翻訳: {text}]")


# ツールリスト
tools = [get_current_time, translate_to_english, translate_to_japanese]

# システムプロンプト
SYSTEM_PROMPT = (
    "あなたは翻訳アシスタントです。"
    "日本語と英語の翻訳、および時刻の取得ができます。"
    "ユーザーの要求に応じて適切なツールを使用してください。"
)


def _create_agent() -> Any:
    """LangChainエージェントを作成する。

    Returns:
        設定済みのAgent。
    """
    # LM Studio or OpenAI API
    # LangChainでは openai/ プレフィックス不要
    model_name = os.getenv("LOCAL_LLM_MODEL", "google/gemma-3n-e4b")
    if model_name.startswith("openai/"):
        model_name = model_name[7:]  # "openai/" を除去

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE,
    )

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )


# エージェントインスタンス（遅延初期化用）
_agent: Any | None = None


def get_agent() -> Any:
    """エージェントのシングルトンインスタンスを取得する。

    Returns:
        Agentインスタンス。
    """
    global _agent
    if _agent is None:
        _agent = _create_agent()
    return _agent


async def invoke_agent(user_message: str) -> str:
    """エージェントを呼び出してレスポンスを取得する。

    Args:
        user_message: ユーザーからのメッセージ。

    Returns:
        エージェントからのレスポンス文字列。
    """
    agent = get_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})

    # 最後のAIメッセージからコンテンツを取得
    messages = result.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            return str(msg.content)

    return "応答を生成できませんでした。"
