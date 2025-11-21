"""
AI-powered article categorization module
Automatically classifies articles into categories using rules and AI
"""

import anthropic
import os
import yaml
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ArticleCategorizer:
    """Categorizes articles using rule-based and AI-powered methods"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        categories_path: str = "config/categories.yaml"
    ):
        """
        Initialize categorizer

        Args:
            api_key: Anthropic API key (if None, reads from env)
            categories_path: Path to categories definition file
        """
        # Load categories
        with open(categories_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            self.categories = config['categories']

        # Initialize Claude client for fallback AI classification
        api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
            logger.warning("No Anthropic API key found - AI categorization disabled")

        logger.info(f"Loaded {len(self.categories)} main categories")

    def categorize(
        self,
        title: str,
        tags: List[str],
        body: str = ""
    ) -> Tuple[str, str]:
        """
        Categorize an article

        Args:
            title: Article title
            tags: List of tags
            body: Article content (optional)

        Returns:
            (category, subcategory) tuple
        """
        # First try rule-based categorization
        category, subcategory = self._rule_based_categorize(title, tags)

        # If rule-based fails and we have body content, try AI
        if category == "other" and self.client and body:
            try:
                category, subcategory = self._ai_categorize(title, tags, body)
            except Exception as e:
                logger.error(f"AI categorization failed: {e}")

        logger.info(f"Categorized as: {category}/{subcategory} - {title}")
        return category, subcategory

    def _rule_based_categorize(
        self,
        title: str,
        tags: List[str]
    ) -> Tuple[str, str]:
        """
        Rule-based categorization using keywords and tags

        Args:
            title: Article title
            tags: List of tags

        Returns:
            (category, subcategory) tuple
        """
        title_lower = title.lower()
        tags_lower = [tag.lower() for tag in tags]

        # Try to match by tags first (most reliable)
        for cat_key, cat_data in self.categories.items():
            for subcat_key, subcat_data in cat_data['subcategories'].items():
                # Check tags
                subcat_tags_lower = [t.lower() for t in subcat_data.get('tags', [])]
                for tag in tags_lower:
                    if tag in subcat_tags_lower:
                        return cat_key, subcat_key

        # Try to match by keywords in title
        for cat_key, cat_data in self.categories.items():
            for subcat_key, subcat_data in cat_data['subcategories'].items():
                # Check keywords
                for keyword in subcat_data.get('keywords', []):
                    if keyword.lower() in title_lower:
                        return cat_key, subcat_key

        # No match found
        return "other", "general"

    def _ai_categorize(
        self,
        title: str,
        tags: List[str],
        body: str
    ) -> Tuple[str, str]:
        """
        AI-powered categorization using Claude

        Args:
            title: Article title
            tags: List of tags
            body: Article body

        Returns:
            (category, subcategory) tuple
        """
        if not self.client:
            return "other", "general"

        # Build category list for prompt
        category_list = []
        for cat_key, cat_data in self.categories.items():
            for subcat_key, subcat_data in cat_data['subcategories'].items():
                category_list.append(
                    f"{cat_key}/{subcat_key} - {subcat_data['name']}"
                )

        prompt = f"""以下の技術記事を最も適切なカテゴリに分類してください。

タイトル: {title}
タグ: {', '.join(tags)}
内容の抜粋: {body[:1000]}

利用可能なカテゴリ:
{chr(10).join(category_list)}

応答は必ず以下の形式でお願いします（他の説明は不要）:
category/subcategory

例: frontend/react

応答:"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=50,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )

            result = message.content[0].text.strip()

            # Parse result
            if '/' in result:
                parts = result.split('/')
                category = parts[0].strip()
                subcategory = parts[1].strip()

                # Validate result
                if category in self.categories:
                    if subcategory in self.categories[category]['subcategories']:
                        return category, subcategory

        except Exception as e:
            logger.error(f"Error in AI categorization: {e}")

        return "other", "general"

    def get_category_info(self, category: str, subcategory: str) -> Dict:
        """
        Get information about a category

        Args:
            category: Main category
            subcategory: Subcategory

        Returns:
            Category information dictionary
        """
        if category in self.categories:
            cat_data = self.categories[category]
            if subcategory in cat_data['subcategories']:
                subcat_data = cat_data['subcategories'][subcategory]
                return {
                    'category': category,
                    'category_name': cat_data['name'],
                    'category_description': cat_data.get('description', ''),
                    'subcategory': subcategory,
                    'subcategory_name': subcat_data['name']
                }

        return {
            'category': category,
            'category_name': category,
            'category_description': '',
            'subcategory': subcategory,
            'subcategory_name': subcategory
        }

    def list_all_categories(self) -> Dict[str, List[str]]:
        """
        List all available categories

        Returns:
            Dictionary mapping category to list of subcategories
        """
        result = {}
        for cat_key, cat_data in self.categories.items():
            result[cat_key] = list(cat_data['subcategories'].keys())
        return result
