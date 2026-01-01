# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Google Agent Development Kit (ADK) を使用したAIエージェント開発のサンプルプロジェクト。A2Aプロトコルによるマルチエージェントオーケストレーション機能付き。

## 開発コマンド

```bash
# 依存関係のインストール
uv sync

# ADK Webインターフェースの起動
uv run adk web src

# LangChain A2Aエージェントの起動（port:8001）
PYTHONPATH=src uv run python -m langchain_agent

# local_llm A2Aサーバーの起動（port:8000）
PYTHONPATH=src uv run python -m local_llm

# 単一Pythonファイルの実行
uv run python <file>

# リント & フォーマット
uv run ruff check .     # リントチェック
uv run ruff check --fix # 自動修正
uv run ruff format .    # フォーマット

# pre-commit（初回のみ）
uv run pre-commit install
```

> **Note**: pre-commit hookにより、コミット時に自動でRuffが実行される

## アーキテクチャ

- **パッケージマネージャー**: uv（pipではなくuvを使用）
- **Python**: 3.12以上
- **フレームワーク**: google-adk, a2a-sdk, langchain

### ディレクトリ構造

```
src/
├── __init__.py           # srcパッケージ化
├── common/               # 共通モジュール
│   ├── tools.py          # 共通ツール（時刻取得、計算）
│   └── a2a_tools.py      # A2Aクライアントツール
├── basic/                # Gemini基本エージェント
│   └── agent.py          # root_agent 定義
├── local_llm/            # AIオーケストレーター（A2A対応）
│   ├── agent.py          # root_agent 定義
│   ├── agent_card.py     # A2A Agent Card
│   ├── agent_executor.py # A2A Executor
│   └── __main__.py       # A2Aサーバー起動
└── langchain_agent/      # LangChain A2Aエージェント
    ├── agent.py          # LangChainエージェント
    ├── agent_card.py     # A2A Agent Card
    ├── agent_executor.py # A2A Executor
    └── __main__.py       # A2Aサーバー起動（port:8001）
```

### エージェント定義パターン

エージェントは `src/<name>/agent.py` に `root_agent` という変数名で定義する：

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="エージェント名",
    model="gemini-2.5-flash-lite",
    description="説明",
    tools=[google_search],  # 使用するツール
    instruction="振る舞いの指示"
)
```

### A2Aオーケストレーション

local_llm（ADK）がオーケストレーターとして、LangChainエージェントをA2Aプロトコルで呼び出す：

```
ADK Web (port:8000) → local_llm → A2A → langchain_agent (port:8001)
```

## 環境変数

`.env` ファイルに以下を設定（`.env.example` を参照）：

```env
# Gemini API
GOOGLE_API_KEY=your-key

# LM Studio（ローカルLLM）
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_API_KEY=not-needed
LOCAL_LLM_MODEL=openai/google/gemma-3n-e4b
```

## Python コーディング規約
@./github/instructions/python.instructions.md
