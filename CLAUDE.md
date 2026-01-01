# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Google Agent Development Kit (ADK) を使用したAIエージェント開発のサンプルプロジェクト。Geminiモデルを活用した日本語AIアシスタントの実装例。

## 開発コマンド

```bash
# 依存関係のインストール
uv sync

# ADK Webインターフェースの起動
uv run adk web src

# 単一Pythonファイルの実行
uv run python <file>
```

## アーキテクチャ

- **パッケージマネージャー**: uv（pipではなくuvを使用）
- **Python**: 3.12以上
- **フレームワーク**: google-adk

### ディレクトリ構造

```
src/
└── <agent_name>/     # 各エージェントは個別ディレクトリ
    └── agent.py      # root_agent を定義（ADKの規約）
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

## 環境変数

`.env` ファイルに `GOOGLE_API_KEY` を設定（`.env.example` を参照）


## Python コーディング規約
@./github/instructions/python.instructions.md
