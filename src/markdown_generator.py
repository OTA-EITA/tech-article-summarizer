"""
Markdown file generator
Creates formatted markdown files from article data
"""

from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Generates markdown files from article data"""

    def generate_category_article(
        self,
        article: Dict,
        category_info: Dict
    ) -> str:
        """
        Generate markdown content for a single article in category structure

        Args:
            article: Article dictionary with summary
            category_info: Category information dict

        Returns:
            Markdown formatted string
        """
        md = f"## [{article['title']}]({article['url']})\n\n"

        # Category badge
        md += f"> 📁 **{category_info['category_name']}** › **{category_info['subcategory_name']}**\n\n"

        # Meta info
        md += "**メタ情報:**\n\n"
        md += f"- 📝 著者: [@{article['author']}]({article['author_url']})\n"

        published_at = article['published_at']
        if isinstance(published_at, str):
            md += f"- 📅 投稿日: {published_at}\n"
        else:
            md += f"- 📅 投稿日: {published_at.strftime('%Y-%m-%d %H:%M')}\n"

        md += f"- ❤️ いいね: {article['likes_count']}\n"
        md += f"- 🔖 ストック: {article.get('stocks_count', 0)}\n"
        md += f"- 🏷️ タグ: {', '.join(article['tags'])}\n"
        md += f"- 🌐 ソース: {article['source'].upper()}\n\n"

        # Summary
        md += "**要約:**\n\n"
        md += f"{article.get('summary', '要約なし')}\n\n"

        # Key points
        if article.get('key_points'):
            md += "**キーポイント:**\n\n"
            for point in article['key_points']:
                md += f"- {point}\n"
            md += "\n"

        # Tech stack
        if article.get('tech_stack'):
            md += "**使用技術:**\n\n"
            for tech in article['tech_stack']:
                md += f"- {tech}\n"
            md += "\n"

        return md

    def generate_daily_report(
        self,
        articles: List[Dict],
        date: datetime
    ) -> str:
        """
        Generate daily article report in markdown (legacy format)

        Args:
            articles: List of summarized articles
            date: Date of the report

        Returns:
            Markdown formatted string
        """
        date_str = date.strftime('%Y-%m-%d')

        # Header
        md = f"# 技術記事まとめ - {date_str}\n\n"
        md += f"> 📅 生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Summary stats
        md += "## 📊 サマリー\n\n"
        md += f"- 記事数: {len(articles)}件\n"

        if articles:
            avg_likes = sum(a['likes_count'] for a in articles) / len(articles)
            md += f"- 平均いいね数: {avg_likes:.1f}\n"

            # Top tags
            all_tags = []
            for article in articles:
                all_tags.extend(article['tags'])

            if all_tags:
                tag_counts = {}
                for tag in all_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

                top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                md += f"- 人気タグ: {', '.join([tag for tag, _ in top_tags])}\n"

        md += "\n---\n\n"

        # Articles
        for i, article in enumerate(articles, 1):
            md += self._format_article(article, i)
            md += "\n---\n\n"

        # Footer
        md += f"*このレポートは自動生成されました*\n"

        return md

    def _format_article(self, article: Dict, index: int) -> str:
        """
        Format single article as markdown

        Args:
            article: Article dictionary with summary
            index: Article number

        Returns:
            Markdown formatted string
        """
        md = f"## {index}. [{article['title']}]({article['url']})\n\n"

        # Meta info
        md += "**メタ情報:**\n\n"
        md += f"- 📝 著者: [@{article['author']}]({article['author_url']})\n"
        md += f"- 📅 投稿日: {article['published_at'].strftime('%Y-%m-%d %H:%M')}\n"
        md += f"- ❤️ いいね: {article['likes_count']}\n"
        md += f"- 🔖 ストック: {article['stocks_count']}\n"
        md += f"- 🏷️ タグ: {', '.join(article['tags'])}\n"
        md += f"- 🌐 ソース: Qiita\n\n"

        # Summary
        md += "**要約:**\n\n"
        md += f"{article['summary']}\n\n"

        # Key points
        if article.get('key_points'):
            md += "**キーポイント:**\n\n"
            for point in article['key_points']:
                md += f"- {point}\n"
            md += "\n"

        # Tech stack
        if article.get('tech_stack'):
            md += "**使用技術:**\n\n"
            for tech in article['tech_stack']:
                md += f"- {tech}\n"
            md += "\n"

        return md

    def generate_category_readme(
        self,
        category_info: Dict,
        articles: List[Dict],
        stats: Optional[Dict] = None
    ) -> str:
        """
        Generate README for category directory

        Args:
            category_info: Category information
            articles: Recent articles in this category
            stats: Optional statistics dictionary

        Returns:
            Markdown formatted string
        """
        md = f"# {category_info['subcategory_name']}\n\n"
        md += f"> {category_info['category_description']}\n\n"

        # Stats
        if stats:
            md += "## 📊 統計情報\n\n"
            md += f"- 総記事数: {stats.get('article_count', 0)}件\n"
            md += f"- 総いいね数: {stats.get('total_likes', 0)}\n"
            md += f"- 最終更新: {stats.get('last_updated', 'N/A')}\n\n"

        # Recent articles
        if articles:
            md += "## 📅 最近の記事\n\n"
            for article in articles[:10]:
                published_at = article.get('published_at', '')
                if isinstance(published_at, datetime):
                    date_str = published_at.strftime('%Y-%m-%d')
                else:
                    date_str = str(published_at)[:10] if published_at else 'N/A'

                md += f"- [{article['title']}]({article['url']}) "
                md += f"- {date_str} ({article['likes_count']} いいね)\n"
            md += "\n"

        md += "---\n\n"
        md += f"*最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return md

    def save_report(
        self,
        content: str,
        filename: str,
        output_dir: str = "articles"
    ) -> str:
        """
        Save markdown content to file

        Args:
            content: Markdown content
            filename: Output filename
            output_dir: Output directory

        Returns:
            Path to saved file
        """
        import os

        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Report saved to: {filepath}")
        return filepath

    def append_to_file(
        self,
        content: str,
        filepath: Path
    ):
        """
        Append content to an existing file

        Args:
            content: Content to append
            filepath: Path to file
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(content)
            f.write("\n\n---\n\n")

        logger.info(f"Appended content to: {filepath}")
