"""A2A AgentExecutor実装（LangChain用）。

LangChainエージェントをA2Aプロトコルで公開するためのExecutor。
"""

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Task, TaskState, TaskStatus, TaskStatusUpdateEvent
from a2a.utils.message import new_agent_text_message

from .agent import invoke_agent


class LangChainA2AExecutor(AgentExecutor):
    """LangChainエージェントのA2A Executor。

    LangChain 1.0+のcreate_agentを使用してエージェントを実行し、
    A2Aプロトコルでレスポンスを返す。
    """

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
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.working),
                final=False,
            )
        )

        try:
            # LangChainエージェントを呼び出し
            response_text = await invoke_agent(user_message)
        except Exception as e:
            response_text = f"エラーが発生しました: {e}"

        # 完了タスクを送信
        await event_queue.enqueue_event(
            Task(
                id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.completed,
                    message=new_agent_text_message(
                        response_text,
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
        await event_queue.enqueue_event(
            Task(
                id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.canceled),
            )
        )
