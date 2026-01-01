"""A2Aクライアントツール。

リモートのA2Aエージェントと通信するためのADKカスタムツール。
"""

import uuid

import httpx
from a2a.client import A2AClient
from a2a.types import (
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)
from google.adk.tools import ToolContext


async def ask_translator_agent(
    query: str,
    tool_context: ToolContext,
) -> str:
    """翻訳エージェント（LangChain A2A）に質問する。

    日英翻訳や現在時刻の取得が可能な翻訳エージェントにリクエストを送信します。

    Args:
        query: エージェントへの質問やリクエスト。
        tool_context: ADKのツールコンテキスト。

    Returns:
        エージェントからの応答テキスト。
    """
    agent_url = "http://localhost:8001"

    async with httpx.AsyncClient(timeout=30.0) as http_client:
        client = A2AClient(httpx_client=http_client, url=agent_url)

        # メッセージを構築
        message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=query))],
        )

        # リクエストを作成
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=message),
        )

        # エージェントに送信
        response = await client.send_message(request)

        # レスポンスからテキストを抽出
        # SendMessageResponse は root に実際のレスポンスを持つ
        actual_response = response.root if hasattr(response, "root") else response

        if hasattr(actual_response, "result"):
            result = actual_response.result
            # Taskの場合
            if hasattr(result, "status") and result.status:
                status = result.status
                if hasattr(status, "message") and status.message:
                    msg = status.message
                    if msg.parts:
                        for part in msg.parts:
                            if hasattr(part, "root") and hasattr(part.root, "text"):
                                return part.root.text
            # Messageの場合
            if hasattr(result, "parts"):
                for part in result.parts:
                    if hasattr(part, "root") and hasattr(part.root, "text"):
                        return part.root.text

        return "エージェントからの応答を取得できませんでした。"


async def list_available_agents(tool_context: ToolContext) -> str:
    """利用可能なA2Aエージェント一覧を取得する。

    Args:
        tool_context: ADKのツールコンテキスト。

    Returns:
        利用可能なエージェントの情報。
    """
    agents = [
        {
            "name": "LangChain Translator",
            "url": "http://localhost:8001",
            "description": "日英翻訳と時刻取得が可能なエージェント",
            "skills": ["翻訳（日→英）", "翻訳（英→日）", "現在時刻取得"],
        }
    ]

    result_lines = ["利用可能なA2Aエージェント:"]
    for agent in agents:
        result_lines.append(f"\n【{agent['name']}】")
        result_lines.append(f"  URL: {agent['url']}")
        result_lines.append(f"  説明: {agent['description']}")
        result_lines.append(f"  スキル: {', '.join(agent['skills'])}")

    return "\n".join(result_lines)
