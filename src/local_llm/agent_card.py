"""ローカルLLMエージェントのAgent Card定義。

A2Aプロトコルでエージェントを公開するためのメタデータを定義する。
"""

from a2a.types import AgentCapabilities, AgentCard, AgentProvider, AgentSkill

agent_card = AgentCard(
    name="Local Assistant",
    description="ローカルLLMで動作する汎用AIアシスタント",
    url="http://localhost:8000",
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
            id="general-assistant",
            name="汎用アシスタント",
            description="質問応答、時刻取得、計算を行います（ローカルLLM使用）",
            tags=["assistant", "local-llm", "japanese", "calculator"],
            examples=[
                "今何時？",
                "123 * 456 を計算して",
                "Pythonについて教えて",
            ],
        ),
    ],
)
