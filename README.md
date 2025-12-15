# ADK Test

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-8E75B2?logo=googlegemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)

[Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) を使用したAIエージェント開発のサンプルプロジェクトです。

## 概要

Google ADK（Agent Development Kit）は、AIエージェントの構築・評価・デプロイを行うためのオープンソースのPythonフレームワークです。本プロジェクトでは、ADKを使った基本的なエージェント実装を紹介します。

### 特徴

- Geminiモデルを使用した基本的なエージェント実装
- カスタムツール連携（Google検索）
- 日本語AIアシスタントのペルソナ設定

## 前提条件

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/)（推奨パッケージマネージャー）
- Google APIキー（`.env`ファイルに設定）

## セットアップ

### インストール

1. リポジトリをクローン：

```bash
git clone <repository-url>
cd adk-test
```

2. 仮想環境の作成と依存関係のインストール：

```bash
uv sync
```

3. 環境変数の設定：

```bash
cp .env.example .env
# .envファイルを編集してGOOGLE_API_KEYを追加
```

### エージェントの実行

ADK Webインターフェースを起動：

```bash
uv run adk web src
```

## プロジェクト構成

```
adk-test/
├── src/
│   └── basic/           # 基本エージェントの例
│       └── agent.py     # エージェント定義
├── pyproject.toml       # プロジェクト設定
└── uv.lock              # 依存関係ロックファイル
```

## エージェントの例

`basic`エージェントは、シンプルなAIアシスタントの実装例です：

```python
from google.adk.agents import Agent

root_agent = Agent(
    name="星野ミライ",
    model="gemini-2.5-flash-lite",
    description="未来から来たAI秘書",
    instruction="..."
)
```

## 参考リンク

- [ADK ドキュメント](https://google.github.io/adk-docs/)
- [ADK Python GitHub](https://github.com/google/adk-python)
- [ADK サンプルエージェント](https://github.com/google/adk-samples)
