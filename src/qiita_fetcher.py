"""
Qiita API fetcher module
Fetches recent articles from Qiita based on configuration
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QiitaFetcher:
    """Fetches articles from Qiita API"""

    def __init__(self, access_token: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize Qiita fetcher

        Args:
            access_token: Qiita access token (if None, reads from env)
            config: Configuration dict with qiita settings
        """
        self.access_token = access_token or os.getenv('QIITA_ACCESS_TOKEN')
        if not self.access_token:
            raise ValueError("QIITA_ACCESS_TOKEN is required")

        self.config = config or {}
        self.base_url = self.config.get('base_url', 'https://qiita.com/api/v2')
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def fetch_recent_articles(
        self,
        days_back: int = 1,
        per_page: int = 20,
        min_likes: int = 10,
        query: str = ""
    ) -> List[Dict]:
        """
        Fetch recent articles from Qiita

        Args:
            days_back: Number of days to look back
            per_page: Number of articles per request (max 100)
            min_likes: Minimum number of likes
            query: Optional search query

        Returns:
            List of article dictionaries
        """
        logger.info(f"Fetching articles from last {days_back} days with min {min_likes} likes")

        # Calculate date threshold
        date_threshold = datetime.now() - timedelta(days=days_back)
        date_str = date_threshold.strftime('%Y-%m-%d')

        # Build query
        search_query = f"created:>={date_str} stocks:>={min_likes}"
        if query:
            search_query = f"{query} {search_query}"

        # Fetch articles
        articles = []
        page = 1

        while True:
            params = {
                'page': page,
                'per_page': min(per_page, 100),
                'query': search_query
            }

            try:
                response = requests.get(
                    f"{self.base_url}/items",
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()

                items = response.json()

                if not items:
                    break

                # Parse articles
                for item in items:
                    article = self._parse_article(item)
                    articles.append(article)

                logger.info(f"Fetched page {page}: {len(items)} articles")

                # For MVP, only fetch first page
                break

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching articles: {e}")
                break

        logger.info(f"Total articles fetched: {len(articles)}")
        return articles

    def _parse_article(self, item: Dict) -> Dict:
        """
        Parse Qiita API response into standardized format

        Args:
            item: Raw API response item

        Returns:
            Parsed article dictionary
        """
        return {
            'source': 'qiita',
            'article_id': item['id'],
            'title': item['title'],
            'url': item['url'],
            'author': item['user']['id'],
            'author_name': item['user']['name'] or item['user']['id'],
            'author_url': f"https://qiita.com/{item['user']['id']}",
            'published_at': datetime.fromisoformat(item['created_at'].replace('Z', '+00:00')),
            'updated_at': datetime.fromisoformat(item['updated_at'].replace('Z', '+00:00')),
            'likes_count': item['likes_count'],
            'stocks_count': item.get('stocks_count', 0),
            'tags': [tag['name'] for tag in item['tags']],
            'body': item.get('body', ''),
            'rendered_body': item.get('rendered_body', ''),
        }

    def get_article_content(self, article_id: str) -> Optional[str]:
        """
        Get full article content by ID

        Args:
            article_id: Qiita article ID

        Returns:
            Article body or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/items/{article_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get('body', '')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching article {article_id}: {e}")
            return None
