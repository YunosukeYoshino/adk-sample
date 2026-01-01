"""A2A AgentExecutor実装。

ローカルLLMエージェントをA2Aプロトコルで公開するためのExecutor。
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Task, TaskState, TaskStatus, TaskStatusUpdateEvent
from a2a.utils.message import new_agent_text_message
from google.adk.agents import RunConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent


class LocalLLMAgentExecutor(AgentExecutor):
    """ローカルLLMエージェントのA2A Executor。

    ADKのRunnerを使用してエージェントを実行し、
    A2Aプロトコルでレスポンスを返す。
    """

    def __init__(self) -> None:
        """Executorを初期化する。"""
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=root_agent,
            app_name="local-llm-agent",
            session_service=self.session_service,
        )
        self.run_config = RunConfig(
            max_llm_calls=10,  # 安全性のため呼び出し回数を制限
        )

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """ユーザーメッセージを処理してレスポンスを返す。

        Args:
            context: A2Aリクエストコンテキスト。
            event_queue: イベントを送信するキュー。
        """
        # ユーザーメッセージを取得
        if not context.message or not context.message.parts:
            return

        user_message = context.message.parts[0].root.text

        # working状態を送信
        await event_queue.put(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.working),
                final=False,
            )
        )

        # セッション取得または作成
        user_id = context.context_id or "default-user"
        session = await self.session_service.get_session(
            app_name="local-llm-agent",
            user_id=user_id,
        )
        if session is None:
            session = await self.session_service.create_session(
                app_name="local-llm-agent",
                user_id=user_id,
            )

        # ADKエージェントを実行
        content = types.Content(
            role="user",
            parts=[types.Part.from_text(user_message)],
        )

        response_text = ""
        async for event in self.runner.run_async(
            session_id=session.id,
            user_id=session.user_id,
            new_message=content,
            run_config=self.run_config,
        ):
            if hasattr(event, "content") and event.content:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text

        # 完了タスクを送信
        await event_queue.put(
            Task(
                id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.completed,
                    message=new_agent_text_message(
                        response_text or "応答を生成できませんでした。",
                        context.context_id,
                        context.task_id,
                    ),
                ),
            )
        )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """タスクをキャンセルする。

        Args:
            context: A2Aリクエストコンテキスト。
            event_queue: イベントを送信するキュー。
        """
        await event_queue.put(
            Task(
                id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.canceled),
            )
        )
