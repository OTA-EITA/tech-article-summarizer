# 🤖 Tech Article Summarizer (MVP)

Qiitaの最新技術記事を自動取得し、Claude AIで要約するツールです。

## ✨ 機能

- ✅ Qiita APIから最新記事を自動取得
- ✅ Claude Sonnet 4で記事を自動要約
- ✅ 見やすいMarkdownレポートを生成
- ✅ いいね数でフィルタリング
- ✅ タグ別サマリー

## 📋 必要要件

- Python 3.8+
- Qiita Access Token
- Anthropic API Key

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
cd tech-article-summarizer
```

### 2. 仮想環境の作成（推奨）

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env` ファイルを作成：

```bash
cp .env.example .env
```

`.env` を編集してAPIキーを設定：

```env
# Qiita API
QIITA_ACCESS_TOKEN=your_qiita_token_here

# Anthropic API
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### APIキーの取得方法

**Qiita Access Token:**
1. [Qiita](https://qiita.com) にログイン
2. 設定 > アプリケーション > 個人用アクセストークン
3. 新しいトークンを生成（読み取り権限のみでOK）

**Anthropic API Key:**
1. [Anthropic Console](https://console.anthropic.com/) にアクセス
2. API Keys から新しいキーを生成

### 5. 設定のカスタマイズ（オプション）

[config/config.yaml](config/config.yaml) を編集して、以下を調整できます：

- `days_back`: 何日前からの記事を取得するか（デフォルト: 1）
- `min_likes`: 最低いいね数（デフォルト: 10）
- `per_page`: 1回で取得する記事数（デフォルト: 20）

## 💻 使い方

### 基本実行

```bash
python src/main.py
```

実行すると、以下の処理が行われます：

1. Qiitaから条件に合う記事を取得
2. Claude APIで各記事を要約
3. `articles/` ディレクトリにMarkdownレポートを保存

### 出力例

`articles/2025-11-22_qiita.md` のような形式で保存されます：

```markdown
# 技術記事まとめ - 2025-11-22

## 📊 サマリー
- 記事数: 15件
- 平均いいね数: 25.3
- 人気タグ: React, TypeScript, Python, AWS, Docker

---

## 1. [React 19の新機能を試してみた](https://qiita.com/...)

**メタ情報:**
- 📝 著者: @user123
- 📅 投稿日: 2025-11-22 10:30
- ❤️ いいね: 42
- 🏷️ タグ: React, JavaScript, Frontend

**要約:**
React 19で導入された新しいServer Componentsの使い方について解説...

**キーポイント:**
- Server Componentsでパフォーマンスが向上
- 新しいuseフックの活用方法
- 既存コードからの移行手順

**使用技術:**
- React 19
- TypeScript
- Next.js 14
```

## 📁 ディレクトリ構造

```
tech-article-summarizer/
├── src/
│   ├── main.py                # メインスクリプト
│   ├── qiita_fetcher.py       # Qiita API連携
│   ├── summarizer.py          # Claude要約機能
│   └── markdown_generator.py  # Markdown生成
├── config/
│   └── config.yaml            # 設定ファイル
├── articles/                  # 生成されたレポート
├── logs/                      # ログファイル
├── .env                       # 環境変数（Git管理外）
├── .env.example               # 環境変数テンプレート
├── requirements.txt           # 依存パッケージ
└── README.md
```

## ⚙️ 設定オプション

### config.yaml

```yaml
qiita:
  per_page: 20          # 取得記事数
  days_back: 1          # 何日前から取得するか
  min_likes: 10         # 最低いいね数
  query: ""             # 検索クエリ（空=全記事）

claude:
  model: "claude-sonnet-4-20250514"
  max_tokens: 1000      # 要約の最大トークン数
  temperature: 0.3      # 生成の多様性（0-1）

output:
  base_dir: "articles"
  filename_format: "{date}_{source}.md"
```

## 🐛 トラブルシューティング

### エラー: "QIITA_ACCESS_TOKEN is required"

`.env` ファイルが正しく設定されているか確認してください。

### エラー: "ANTHROPIC_API_KEY is required"

Anthropic APIキーが設定されているか確認してください。

### 記事が取得できない

- `config.yaml` の `min_likes` を下げてみてください
- `days_back` を増やしてみてください
- Qiita APIのレート制限に達していないか確認してください

### 要約が生成されない

- Anthropic APIの残高を確認してください
- ログファイル（`logs/app.log`）でエラー詳細を確認してください

## 💰 コスト見積もり

### Claude API使用量（目安）

- 1記事あたり: 約 2,000トークン（入力） + 500トークン（出力）
- 20記事処理: 約 40,000 入力 + 10,000 出力
- Claude Sonnet 4の料金: 入力 $3/1M、出力 $15/1M

**概算コスト（1日20記事）:**
- 入力: 0.04M × $3 = $0.12
- 出力: 0.01M × $15 = $0.15
- **合計: 約 $0.27/日**

月間（30日）: 約 $8.10

## 🚀 次のステップ

このMVPが動作したら、以下の機能を追加できます：

- [ ] カテゴリ自動分類（AI）
- [ ] SQLiteでの重複記事チェック
- [ ] Zenn記事の取得
- [ ] GitHub Actionsでの自動実行
- [ ] 週次・月次サマリーレポート
- [ ] カテゴリ別ディレクトリ整理

## 📝 ログ

実行ログは `logs/app.log` に保存されます。

```bash
tail -f logs/app.log  # リアルタイムでログを確認
```

## 📄 ライセンス

MIT License

## 🤝 貢献

Issue や Pull Request を歓迎します！

---

**注意:** このツールは技術学習・情報収集を目的としています。APIの利用規約を遵守してください。
