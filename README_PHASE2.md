# 🤖 Tech Article Summarizer - Phase 2

Qiitaの最新技術記事を自動取得し、**AIでカテゴリ自動分類**、Claude AIで要約するツールです。

## 🆕 Phase 2の新機能

✅ **AIによる自動カテゴリ分類**
- 記事のタイトル・タグ・内容から自動でカテゴリ判定
- フロントエンド、バックエンド、クラウド、DevOpsなど8つの主要カテゴリ
- 各カテゴリ内でさらに細かく分類（例: フロントエンド → React, Vue, etc.）

✅ **SQLiteデータベース管理**
- 記事の重複チェック（同じ記事を二重登録しない）
- カテゴリ別統計情報の自動集計
- 記事の履歴管理

✅ **カテゴリ別ディレクトリ構造**
- カテゴリ/サブカテゴリごとにファイル整理
- 年月ごとの自動フォルダ分け
- 各カテゴリにREADME自動生成

## 📋 必要要件

- Python 3.8+
- Qiita Access Token
- Anthropic API Key

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env` ファイルを作成：

```bash
cp .env.example .env
```

`.env` を編集してAPIキーを設定：

```env
QIITA_ACCESS_TOKEN=your_qiita_token_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. 設定のカスタマイズ（オプション）

[config/config.yaml](config/config.yaml) を編集

## 💻 使い方

### 基本実行

```bash
python src/main.py
```

### 実行の流れ

1. ✅ Qiitaから記事取得
2. 🔍 データベースで重複チェック
3. 🤖 AIで各記事をカテゴリ分類
4. 📝 Claudeで要約生成
5. 💾 カテゴリ別ディレクトリに保存
6. 📊 カテゴリREADMEを自動更新

### 出力例

```
tech-article-summarizer/
├── articles/
│   ├── frontend/
│   │   ├── react/
│   │   │   ├── 2025-11/
│   │   │   │   └── 2025-11-22.md    ← React記事はここ
│   │   │   └── README.md             ← 自動生成
│   │   ├── vue/
│   │   └── README.md
│   ├── backend/
│   │   ├── python/
│   │   │   ├── 2025-11/
│   │   │   │   └── 2025-11-22.md    ← Python記事はここ
│   │   │   └── README.md
│   │   └── nodejs/
│   └── ai-ml/
│       └── llm/
│           ├── 2025-11/
│           │   └── 2025-11-22.md    ← LLM記事はここ
│           └── README.md
└── data/
    └── articles.db                   ← SQLiteデータベース
```

## 📁 ディレクトリ構造

```
tech-article-summarizer/
├── src/
│   ├── main.py                # メインスクリプト (Phase 2対応)
│   ├── qiita_fetcher.py       # Qiita API連携
│   ├── summarizer.py          # Claude要約機能
│   ├── categorizer.py         # 🆕 AIカテゴリ分類
│   ├── database.py            # 🆕 SQLite管理
│   ├── path_builder.py        # 🆕 パス生成
│   └── markdown_generator.py  # Markdown生成 (拡張版)
├── config/
│   ├── config.yaml            # 基本設定
│   └── categories.yaml        # 🆕 カテゴリ定義
├── articles/                  # 🆕 カテゴリ別ディレクトリ
├── data/                      # 🆕 データベース
├── logs/                      # ログファイル
└── README.md
```

## 🗂️ カテゴリ一覧

### 1. **フロントエンド** (`frontend`)
- React
- Vue.js
- Angular
- その他（HTML/CSS/JavaScript/TypeScript）

### 2. **バックエンド** (`backend`)
- Python (Django/Flask/FastAPI)
- Node.js (Express/NestJS)
- Go
- Ruby (Rails)
- Java (Spring)
- PHP (Laravel)

### 3. **クラウド** (`cloud`)
- AWS
- Google Cloud
- Azure

### 4. **DevOps** (`devops`)
- Docker
- Kubernetes
- CI/CD
- Terraform

### 5. **データベース** (`database`)
- SQL (MySQL/PostgreSQL)
- NoSQL (MongoDB/Redis/DynamoDB)

### 6. **AI・機械学習** (`ai-ml`)
- 機械学習
- 深層学習
- 大規模言語モデル (LLM/ChatGPT/Claude)

### 7. **モバイル** (`mobile`)
- iOS (Swift)
- Android (Kotlin)
- Flutter
- React Native

### 8. **その他** (`other`)
- 分類不能な記事

## ⚙️ カテゴリのカスタマイズ

[config/categories.yaml](config/categories.yaml) を編集することで、独自のカテゴリを追加できます：

```yaml
categories:
  my-category:
    name: "マイカテゴリ"
    description: "カスタムカテゴリの説明"
    subcategories:
      my-subcat:
        name: "マイサブカテゴリ"
        keywords: ["keyword1", "keyword2"]
        tags: ["Tag1", "Tag2"]
```

## 📊 データベーススキーマ

### articles テーブル
記事の基本情報と分類を保存

| カラム | 説明 |
|--------|------|
| source | 記事ソース (qiita, zenn) |
| article_id | 記事の一意ID |
| title | タイトル |
| category | カテゴリ |
| subcategory | サブカテゴリ |
| file_path | 保存先パス |
| tags | タグ (JSON) |
| likes_count | いいね数 |

### category_stats テーブル
カテゴリ別統計情報

| カラム | 説明 |
|--------|------|
| category | カテゴリ |
| subcategory | サブカテゴリ |
| article_count | 記事数 |
| total_likes | 総いいね数 |

## 🐛 トラブルシューティング

### カテゴリが正しく分類されない

1. [config/categories.yaml](config/categories.yaml) のキーワード・タグを調整
2. より多くの記事内容を渡すように `main.py` の `body[:1000]` を増やす
3. AI分類を使う場合、Anthropic APIキーが設定されているか確認

### データベースエラー

```bash
# データベースをリセット
rm data/articles.db
python src/main.py
```

### 実行時のログ確認

```bash
tail -f logs/app.log
```

## 💰 コスト見積もり

### Phase 2での追加コスト

**カテゴリ分類:**
- ルールベースでマッチ → 無料
- AI分類（フォールバック）→ 1記事あたり約 $0.001

**要約生成:**
- 1記事あたり約 $0.01

**1日20記事処理:**
- カテゴリ分類: $0.02 (ほとんどルールベースで0円)
- 要約: $0.20
- **合計: 約 $0.22/日**

月間（30日）: 約 $6.60

## 🔄 Phase 1からの移行

Phase 1（MVP）から移行する場合：

1. 新しいファイルを配置
2. `pip install -r requirements.txt` で依存関係を更新
3. `python src/main.py` を実行

既存の記事は自動的にスキップされ、新しい記事のみ処理されます。

## 🚀 次のステップ: Phase 3

- [ ] GitHub Actionsで自動実行
- [ ] 週次・月次サマリーレポート
- [ ] Zenn記事の取得
- [ ] Webダッシュボード

## 📝 ライセンス

MIT License

---

**Phase 2完成！** 🎉

カテゴリ自動分類とデータベース管理により、より整理された形で技術記事を収集できるようになりました。
