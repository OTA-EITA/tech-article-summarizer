# 🤖 Tech Article Summarizer

Qiitaの最新技術記事を自動取得し、AIでカテゴリ分類・Claude AIで要約するツールです。

## ✨ 機能

### Phase 1 (MVP)
- ✅ Qiita API連携で記事取得
- ✅ Claude APIで記事要約
- ✅ Markdownレポート生成

### Phase 2
- ✅ **AIによる自動カテゴリ分類**（8カテゴリ × 25+サブカテゴリ）
- ✅ **SQLiteデータベース管理**（重複チェック・統計情報）
- ✅ **カテゴリ別ディレクトリ構造**（自動整理・README生成）

### Phase 3 🆕
- ✅ **GitHub Actions自動化**（日次自動実行）
- ✅ **手動実行ワークフロー**（パラメータ指定可能）

## 📋 必要要件

- Python 3.8+
- Qiita Access Token
- Anthropic API Key

## 🚀 セットアップ

### ローカル実行

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. 環境変数を設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定

# 3. 実行
python src/main.py
```

### GitHub Actions自動実行

GitHub Actionsで毎日自動実行する場合は、[GitHub Actionsセットアップガイド](docs/GITHUB_ACTIONS_SETUP.md)を参照してください。

**簡単な手順:**
1. GitHubリポジトリの Settings > Secrets で以下を設定
   - `QIITA_ACCESS_TOKEN`
   - `ANTHROPIC_API_KEY`
2. Actions タブから手動実行してテスト
3. 毎日自動で記事が収集されます

## 📁 ディレクトリ構造

```
tech-article-summarizer/
├── .github/workflows/       # 🆕 GitHub Actionsワークフロー
│   ├── daily-fetch.yml      # 日次自動実行
│   └── manual-run.yml       # 手動実行
├── src/
│   ├── main.py              # メインスクリプト
│   ├── qiita_fetcher.py     # Qiita API連携
│   ├── summarizer.py        # Claude要約
│   ├── categorizer.py       # AIカテゴリ分類
│   ├── database.py          # SQLite管理
│   ├── path_builder.py      # パス生成
│   └── markdown_generator.py # Markdown生成
├── config/
│   ├── config.yaml          # 基本設定
│   └── categories.yaml      # カテゴリ定義
├── articles/                # カテゴリ別記事保存先
├── data/                    # データベース
├── docs/                    # ドキュメント
└── logs/                    # ログファイル
```

## 🗂️ カテゴリ一覧

1. **フロントエンド** - React, Vue.js, Angular, etc.
2. **バックエンド** - Python, Node.js, Go, Ruby, Java, PHP
3. **クラウド** - AWS, GCP, Azure
4. **DevOps** - Docker, Kubernetes, CI/CD, Terraform
5. **データベース** - SQL, NoSQL
6. **AI・機械学習** - 機械学習, 深層学習, LLM
7. **モバイル** - iOS, Android, Flutter, React Native
8. **その他** - 分類不能な記事

詳細は [config/categories.yaml](config/categories.yaml) を参照

## 💻 使い方

### ローカル実行

```bash
python src/main.py
```

実行すると：
1. Qiitaから記事取得
2. 重複チェック
3. AIでカテゴリ分類
4. Claudeで要約生成
5. カテゴリ別に保存
6. README自動更新

### GitHub Actions

#### 自動実行（デフォルト）
毎日 00:00 UTC (09:00 JST) に自動実行

#### 手動実行
```
Actions > Manual Run > Run workflow
```

パラメータ:
- `days_back`: 何日前から取得（デフォルト: 1）
- `min_likes`: 最低いいね数（デフォルト: 10）

## ⚙️ 設定

### config.yaml

```yaml
qiita:
  per_page: 20          # 取得記事数
  days_back: 1          # 何日前から
  min_likes: 10         # 最低いいね数

claude:
  model: "claude-sonnet-4-20250514"
  max_tokens: 1000
  temperature: 0.3
```

### categories.yaml

カテゴリのカスタマイズが可能です。
詳細は [README_PHASE2.md](README_PHASE2.md) を参照

## 💰 コスト見積もり

### Claude API（1日20記事）
- 要約生成: $0.20
- カテゴリ分類: $0.02（ほぼルールベースで無料）
- **合計: 約 $0.22/日**

月間（30日）: 約 $6.60

### GitHub Actions
- Publicリポジトリ: 無制限
- Privateリポジトリ: 月2,000分まで無料

## 📊 出力例

```
articles/
├── frontend/
│   └── react/
│       ├── 2025-11/
│       │   └── 2025-11-22.md
│       └── README.md
├── backend/
│   └── python/
│       ├── 2025-11/
│       │   └── 2025-11-22.md
│       └── README.md
└── ai-ml/
    └── llm/
        ├── 2025-11/
        │   └── 2025-11-22.md
        └── README.md
```

## 🐛 トラブルシューティング

### ローカル実行

```bash
# 環境変数が読み込まれない
source venv/bin/activate
python-dotenv が必要

# データベースエラー
rm data/articles.db
python src/main.py

# ログ確認
tail -f logs/app.log
```

### GitHub Actions

詳細は [GitHub Actionsセットアップガイド](docs/GITHUB_ACTIONS_SETUP.md) を参照

## 📚 ドキュメント

- [README_PHASE2.md](README_PHASE2.md) - Phase 2の詳細機能
- [docs/GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md) - GitHub Actions設定ガイド

## 🚀 次のステップ

- [ ] 週次サマリーレポート
- [ ] Zenn記事対応
- [ ] Slack/Discord通知
- [ ] Webダッシュボード

## 📝 ライセンス

MIT License

## 🤝 貢献

Issue や Pull Request を歓迎します！
