#!/usr/bin/env python3
"""
Tech Article Summarizer - Phase 2
Main entry point with categorization and database support
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from qiita_fetcher import QiitaFetcher
from zenn_fetcher import ZennFetcher
from summarizer import ArticleSummarizer
from markdown_generator import MarkdownGenerator
from categorizer import ArticleCategorizer
from database import ArticleDatabase
from path_builder import ArticlePathBuilder


def setup_logging(config: dict):
    """Setup logging configuration"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create logs directory
    os.makedirs('logs', exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config() -> dict:
    """Load configuration from yaml file"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def update_category_readmes(
    db: ArticleDatabase,
    categorizer: ArticleCategorizer,
    md_generator: MarkdownGenerator,
    path_builder: ArticlePathBuilder
):
    """Update README files for all categories"""
    logger = logging.getLogger(__name__)
    logger.info("Updating category READMEs...")

    categories = db.get_all_categories()

    for category, subcategory in categories:
        try:
            # Get category info
            category_info = categorizer.get_category_info(category, subcategory)

            # Get recent articles
            articles = db.get_articles_by_category(category, subcategory, limit=20)

            # Get stats
            stats = db.get_category_stats(category, subcategory)

            # Generate README
            readme_content = md_generator.generate_category_readme(
                category_info,
                articles,
                stats
            )

            # Save README
            readme_path = path_builder.get_category_readme_path(category, subcategory)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)

            logger.info(f"Updated README: {readme_path}")

        except Exception as e:
            logger.error(f"Error updating README for {category}/{subcategory}: {e}")


def main():
    """Main execution flow"""
    print("🚀 Tech Article Summarizer - Phase 2\n")
    print("📦 新機能: カテゴリ自動分類 + データベース管理\n")

    # Load environment variables
    load_dotenv()

    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("Starting Tech Article Summarizer - Phase 2")
    logger.info("=" * 60)

    try:
        # Initialize components
        logger.info("Initializing components...")

        qiita_config = config.get('qiita', {})
        zenn_config = config.get('zenn', {})
        claude_config = config.get('claude', {})
        output_config = config.get('output', {})

        summarizer = ArticleSummarizer(config=claude_config)
        categorizer = ArticleCategorizer()
        md_generator = MarkdownGenerator()
        path_builder = ArticlePathBuilder(output_config.get('base_dir', 'articles'))

        # Initialize database
        db = ArticleDatabase()

        print("✅ コンポーネント初期化完了\n")

        # Fetch articles from multiple sources
        articles = []

        # Fetch from Qiita
        if qiita_config.get('enabled', True):
            logger.info("Fetching articles from Qiita...")
            print("📡 Qiitaから記事を取得中...\n")

            qiita_fetcher = QiitaFetcher(config=qiita_config)
            qiita_articles = qiita_fetcher.fetch_recent_articles(
                days_back=qiita_config.get('days_back', 1),
                per_page=qiita_config.get('per_page', 20),
                min_likes=qiita_config.get('min_likes', 10),
                query=qiita_config.get('query', '')
            )
            articles.extend(qiita_articles)
            print(f"  Qiita: {len(qiita_articles)}件\n")

        # Fetch from Zenn
        if zenn_config.get('enabled', True):
            logger.info("Fetching articles from Zenn...")
            print("📡 Zennから記事を取得中...\n")

            zenn_fetcher = ZennFetcher(config=zenn_config)
            zenn_articles = zenn_fetcher.fetch_recent_articles(
                days_back=zenn_config.get('days_back', 1),
                max_articles=zenn_config.get('max_articles', 50)
            )
            articles.extend(zenn_articles)
            print(f"  Zenn: {len(zenn_articles)}件\n")

            # Fetch from Zenn topics if specified
            topics = zenn_config.get('topics', [])
            if topics:
                for topic in topics:
                    topic_articles = zenn_fetcher.fetch_topic_articles(
                        topic=topic,
                        days_back=zenn_config.get('days_back', 7),
                        max_articles=20
                    )
                    articles.extend(topic_articles)
                    print(f"  Zenn ({topic}): {len(topic_articles)}件\n")

        if not articles:
            logger.warning("No articles found matching criteria")
            print("⚠️  条件に合う記事が見つかりませんでした\n")
            db.close()
            return

        print(f"✅ 合計 {len(articles)}件の記事を取得しました\n")

        # Filter out duplicates
        new_articles = []
        for article in articles:
            if not db.article_exists(article['source'], article['article_id']):
                new_articles.append(article)
            else:
                logger.info(f"Skipping duplicate: {article['title']}")

        if not new_articles:
            print("ℹ️  新しい記事はありませんでした（すべて既存）\n")
            db.close()
            return

        print(f"🆕 新しい記事: {len(new_articles)}件\n")

        # Process each article
        print("⚙️  記事を処理中...\n")

        processed_count = 0
        category_counts = {}

        for i, article in enumerate(new_articles, 1):
            try:
                print(f"[{i}/{len(new_articles)}] {article['title'][:50]}...")

                # Categorize
                category, subcategory = categorizer.categorize(
                    article['title'],
                    article['tags'],
                    article.get('body', '')[:1000]
                )

                category_info = categorizer.get_category_info(category, subcategory)
                logger.info(f"  → {category}/{subcategory}")

                # Summarize
                summary_data = summarizer.summarize(article)
                article.update(summary_data)

                # Generate file path
                file_path = path_builder.get_article_path(
                    category,
                    subcategory,
                    article['published_at']
                )

                # Generate markdown
                article_md = md_generator.generate_category_article(article, category_info)

                # Append to file
                md_generator.append_to_file(article_md, file_path)

                # Save to database
                db.add_article(article, category, subcategory, str(file_path))

                # Track stats
                cat_key = f"{category}/{subcategory}"
                category_counts[cat_key] = category_counts.get(cat_key, 0) + 1

                processed_count += 1
                print(f"  ✓ 保存完了: {category_info['subcategory_name']}\n")

            except Exception as e:
                logger.error(f"Error processing article: {article['title']}", exc_info=e)
                print(f"  ✗ エラー: {str(e)}\n")
                continue

        print("\n" + "=" * 60)
        print(f"📊 処理結果\n")
        print(f"  処理件数: {processed_count}件")
        print(f"\n  カテゴリ別:")
        for cat, count in sorted(category_counts.items()):
            print(f"    - {cat}: {count}件")
        print("=" * 60 + "\n")

        # Update category READMEs
        if processed_count > 0:
            print("📝 カテゴリREADMEを更新中...\n")
            update_category_readmes(db, categorizer, md_generator, path_builder)
            print("✅ README更新完了\n")

        # Close database
        db.close()

        # Summary
        logger.info("=" * 60)
        logger.info("Completed successfully")
        logger.info(f"Articles processed: {processed_count}")
        logger.info(f"Categories: {len(category_counts)}")
        logger.info("=" * 60)

        print("🎉 すべての処理が完了しました！\n")

    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        print(f"\n❌ エラーが発生しました: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
