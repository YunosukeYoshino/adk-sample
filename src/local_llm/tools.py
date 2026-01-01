"""ローカルLLMエージェント用カスタムツール定義。

このモジュールは、エージェントが使用するカスタムツールを提供する。
ToolContextを使用した状態管理を含む。
"""

from datetime import datetime
from typing import Any

from google.adk.tools.tool_context import ToolContext


def get_current_time(tool_context: ToolContext) -> str:
    """現在時刻を取得する。

    ToolContextを使用して、時刻取得の履歴を状態に保存する。

    Args:
        tool_context: ツール実行のコンテキスト。

    Returns:
        日本語フォーマットの現在時刻文字列。
    """
    now = datetime.now()

    # 状態に履歴を保存
    if "time_queries" not in tool_context.state:
        tool_context.state["time_queries"] = []
    tool_context.state["time_queries"].append(now.isoformat())

    return now.strftime("%Y年%m月%d日 %H時%M分%S秒")


def calculate(expression: str) -> str:
    """数式を安全に計算する。

    セキュリティのため、組み込み関数へのアクセスを制限した環境で
    数式を評価する。

    Args:
        expression: 計算する数式（例: "1 + 2 * 3"）。

    Returns:
        計算結果またはエラーメッセージ。
    """
    # 許可する演算子と関数
    allowed_names: dict[str, Any] = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
    }

    try:
        # 安全な評価環境
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return "エラー: ゼロ除算はできません"
    except SyntaxError:
        return f"エラー: 数式の構文が正しくありません: {expression}"
    except Exception as e:
        return f"計算エラー: {e}"
