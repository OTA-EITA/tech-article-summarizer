"""
Article summarization module using Claude API
Generates concise summaries and key points from technical articles
"""

import os
import anthropic
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ArticleSummarizer:
    """Summarizes articles using Claude AI"""

    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize summarizer

        Args:
            api_key: Anthropic API key (if None, reads from env)
            config: Configuration dict with claude settings
        """
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.config = config or {}
        self.model = self.config.get('model', 'claude-sonnet-4-20250514')
        self.max_tokens = self.config.get('max_tokens', 1000)
        self.temperature = self.config.get('temperature', 0.3)

    def summarize(self, article: Dict) -> Dict:
        """
        Generate summary for an article

        Args:
            article: Article dictionary with title, body, tags, etc.

        Returns:
            Dictionary with summary, key_points, and tech_stack
        """
        logger.info(f"Summarizing: {article['title']}")

        prompt = self._build_prompt(article)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text
            summary_data = self._parse_response(response_text)

            logger.info(f"Successfully summarized: {article['title']}")
            return summary_data

        except Exception as e:
            logger.error(f"Error summarizing article: {e}")
            return {
                'summary': 'エラー: 要約の生成に失敗しました',
                'key_points': [],
                'tech_stack': []
            }

    def _build_prompt(self, article: Dict) -> str:
        """
        Build prompt for Claude API

        Args:
            article: Article dictionary

        Returns:
            Formatted prompt string
        """
        title = article['title']
        tags = ', '.join(article['tags'])
        body = article['body'][:5000]  # Limit to first 5000 chars for MVP

        prompt = f"""以下の技術記事を要約してください。

# 記事情報
- タイトル: {title}
- タグ: {tags}

# 記事本文
{body}

# 要求事項
以下の形式で応答してください：

## 要約
（3-4文で記事の内容を簡潔にまとめてください）

## キーポイント
- （重要なポイント1）
- （重要なポイント2）
- （重要なポイント3）

## 技術スタック
- （使用されている技術1）
- （使用されている技術2）

注意：
- 専門用語はそのまま使用してください
- 実装の詳細よりも、何ができるか・何を解決するかを重視してください
- コードスニペットは含めないでください
"""
        return prompt

    def _parse_response(self, response: str) -> Dict:
        """
        Parse Claude's response into structured data

        Args:
            response: Raw response text

        Returns:
            Parsed dictionary
        """
        lines = response.strip().split('\n')

        summary = []
        key_points = []
        tech_stack = []

        current_section = None

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Detect sections
            if '## 要約' in line or '##要約' in line:
                current_section = 'summary'
                continue
            elif '## キーポイント' in line or '##キーポイント' in line:
                current_section = 'key_points'
                continue
            elif '## 技術スタック' in line or '##技術スタック' in line:
                current_section = 'tech_stack'
                continue

            # Skip markdown headers
            if line.startswith('#'):
                continue

            # Add content to appropriate section
            if current_section == 'summary':
                if line and not line.startswith('-'):
                    summary.append(line)
            elif current_section == 'key_points':
                if line.startswith('-') or line.startswith('•'):
                    key_points.append(line.lstrip('-•').strip())
            elif current_section == 'tech_stack':
                if line.startswith('-') or line.startswith('•'):
                    tech_stack.append(line.lstrip('-•').strip())

        return {
            'summary': ' '.join(summary) if summary else 'No summary available',
            'key_points': key_points,
            'tech_stack': tech_stack
        }

    def summarize_batch(self, articles: List[Dict]) -> List[Dict]:
        """
        Summarize multiple articles

        Args:
            articles: List of article dictionaries

        Returns:
            List of articles with added summary data
        """
        logger.info(f"Summarizing {len(articles)} articles...")

        summarized_articles = []

        for i, article in enumerate(articles, 1):
            logger.info(f"Processing {i}/{len(articles)}")

            summary_data = self.summarize(article)

            # Merge summary data into article
            article_with_summary = {**article, **summary_data}
            summarized_articles.append(article_with_summary)

        return summarized_articles
