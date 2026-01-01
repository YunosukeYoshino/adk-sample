# ADK Sample

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-local_LLM-FF6B6B)](https://docs.litellm.ai/)

[Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) を使用したAIエージェント開発のサンプルプロジェクトです。Geminiモデルまたはローカルで動作するLLMを使用した日本語AIアシスタントの実装例を提供します。

[概要](#概要) • [特徴](#特徴) • [セットアップ](#セットアップ) • [使い方](#使い方) • [プロジェクト構成](#プロジェクト構成) • [参考リンク](#参考リンク)

## 概要

Google ADK（Agent Development Kit）は、AIエージェントの構築・評価・デプロイを行うためのオープンソースのPythonフレームワークです。本プロジェクトでは、ADKを使った以下の実装パターンを紹介します：

- **Geminiモデルを使用したクラウドエージェント** - Google Cloud上のGemini APIを活用
- **ローカルLLMを使用したエージェント** - LM Studio + LiteLLMで完全オフライン動作

## 特徴

- Gemini 2.5 Flash を使用した高速応答
- Google検索ツールの統合
- 日本語AIアシスタントのペルソナ設定（星野ミライ）
- LiteLLMによるローカルLLM対応（LM Studio等）
- ADK Webインターフェースによる対話的な開発

## 前提条件

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/)（推奨パッケージマネージャー）
- Google APIキー（Geminiを使用する場合）または [LM Studio](https://lmstudio.ai/)（ローカルLLMを使用する場合）

## セットアップ

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd adk-sample
```

### 2. 依存関係のインストール

```bash
uv sync
```

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集し、使用するモデルに応じて設定：

**Gemini API を使用する場合：**

```env
GOOGLE_API_KEY=your-google-api-key-here
```

**LM Studio（ローカルLLM）を使用する場合：**

```env
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_API_KEY=not-needed
LOCAL_LLM_MODEL=openai/google/gemma-3n-e4b
```

> [!TIP]
> LM Studioで使用するモデル名は `LOCAL_LLM_MODEL` に `openai/<model-name>` 形式で指定します。

## 使い方

### ADK Webインターフェースの起動

```bash
uv run adk web src
```

ブラウザで `http://localhost:8000` を開くと、エージェントと対話できます。

### 利用可能なエージェント

| エージェント | 説明 | モデル |
|:--|:--|:--|
| `basic` | 星野ミライ - Google検索機能付きAI秘書 | Gemini 2.5 Flash Lite |
| `local_llm` | ローカルLLM対応の汎用アシスタント | LM Studio経由 |

## プロジェクト構成

```
adk-sample/
├── src/
│   ├── basic/              # Geminiを使用した基本エージェント
│   │   └── agent.py        # 「星野ミライ」エージェント定義
│   └── local_llm/          # ローカルLLM対応エージェント
│       └── agent.py        # LiteLLM経由のエージェント定義
├── docs/
│   └── PLAN.md             # 機能拡張計画
├── pyproject.toml          # プロジェクト設定
└── uv.lock                 # 依存関係ロックファイル
```

### エージェント定義の例

ADKでは `src/<agent_name>/agent.py` に `root_agent` 変数を定義します：

```python
from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="星野ミライ",
    model="gemini-2.5-flash-lite",
    description="未来から来たAI秘書",
    tools=[google_search],
    instruction="ユーザーの質問に親切に回答します"
)
```

## 開発

```bash
# リント
uv run ruff check .

# 自動修正
uv run ruff check --fix

# フォーマット
uv run ruff format .

# pre-commitフックのインストール（初回のみ）
uv run pre-commit install
```

## 参考リンク

### Google ADK
- [ADK ドキュメント](https://google.github.io/adk-docs/)
- [ADK Python GitHub](https://github.com/google/adk-python)
- [ADK サンプルエージェント](https://github.com/google/adk-samples)

### 関連ツール
- [LiteLLM](https://docs.litellm.ai/) - 100以上のLLMプロバイダーへの統一インターフェース
- [LM Studio](https://lmstudio.ai/) - ローカルLLM実行環境
- [uv](https://docs.astral.sh/uv/) - 高速Pythonパッケージマネージャー
