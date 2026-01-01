"""LangChainエージェントのAgent Card定義。

A2Aプロトコルでエージェントを公開するためのメタデータを定義する。
"""

from a2a.types import AgentCapabilities, AgentCard, AgentProvider, AgentSkill

agent_card = AgentCard(
    name="LangChain Translator",
    description="LangChainで構築された翻訳エージェント。日英翻訳と時刻取得が可能。",
    url="http://localhost:8001",
    version="1.0.0",
    provider=AgentProvider(
        organization="ADK Sample Project",
        url="https://github.com/your-repo/adk-sample",
    ),
    capabilities=AgentCapabilities(
        streaming=True,
        pushNotifications=False,
        stateTransitionHistory=False,
    ),
    defaultInputModes=["text/plain", "application/json"],
    defaultOutputModes=["text/plain", "application/json"],
    skills=[
        AgentSkill(
            id="translation",
            name="翻訳",
            description="日本語と英語の相互翻訳を行います",
            tags=["translation", "japanese", "english", "langchain"],
            examples=[
                "こんにちはを英語に翻訳して",
                "Helloを日本語に翻訳して",
                "今何時？",
            ],
        ),
    ],
)
