"""A2Aサーバー起動スクリプト。

uvicornを使用してA2Aサーバーを起動する。
"""

import uvicorn
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from .agent_card import agent_card
from .agent_executor import LocalLLMAgentExecutor


def main() -> None:
    """A2Aサーバーを起動する。"""
    # コンポーネントの初期化
    agent_executor = LocalLLMAgentExecutor()
    task_store = InMemoryTaskStore()

    # RequestHandlerの作成
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=task_store,
    )

    # A2Aアプリケーションの構築
    app_builder = A2AFastAPIApplication(agent_card, request_handler)
    app = app_builder.build()

    # サーバー起動
    print("A2Aサーバーを起動します: http://localhost:8000")
    print("Agent Card: http://localhost:8000/.well-known/agent-card.json")
    print("JSON-RPC エンドポイント: POST http://localhost:8000/rpc")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
