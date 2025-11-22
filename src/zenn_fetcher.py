"""
Zenn RSS fetcher module
Fetches recent articles from Zenn via RSS feed
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re

logger = logging.getLogger(__name__)


class ZennFetcher:
    """Fetches articles from Zenn RSS feed"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Zenn fetcher

        Args:
            config: Configuration dict with zenn settings
        """
        self.config = config or {}
        self.rss_url = self.config.get('rss_url', 'https://zenn.dev/feed')

    def fetch_recent_articles(
        self,
        days_back: int = 1,
        max_articles: int = 50,
        min_likes: int = 10
    ) -> List[Dict]:
        """
        Fetch recent articles from Zenn RSS

        Args:
            days_back: Number of days to look back
            max_articles: Maximum number of articles to fetch
            min_likes: Minimum number of likes (not available in RSS, kept for compatibility)

        Returns:
            List of article dictionaries
        """
        logger.info(f"Fetching articles from Zenn (last {days_back} days)")

        try:
            response = requests.get(self.rss_url, timeout=30)
            response.raise_for_status()

            # Parse RSS XML
            root = ET.fromstring(response.content)

            articles = []
            date_threshold = datetime.now() - timedelta(days=days_back)

            # Find all items in RSS feed
            for item in root.findall('.//item')[:max_articles]:
                article = self._parse_rss_item(item)

                if article and article['published_at'] >= date_threshold:
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from Zenn")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Zenn RSS: {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"Error parsing RSS XML: {e}")
            return []

    def _parse_rss_item(self, item: ET.Element) -> Optional[Dict]:
        """
        Parse RSS item into standardized format

        Args:
            item: XML Element representing RSS item

        Returns:
            Parsed article dictionary or None
        """
        try:
            # Extract basic fields
            title_elem = item.find('title')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            creator_elem = item.find('{http://purl.org/dc/elements/1.1/}creator')
            description_elem = item.find('description')

            if not all([title_elem, link_elem, pub_date_elem]):
                return None

            title = title_elem.text
            url = link_elem.text
            pub_date_str = pub_date_elem.text

            # Parse publication date
            # Format: "Mon, 22 Nov 2025 12:00:00 +0900"
            published_at = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')

            # Extract article ID from URL
            # URL format: https://zenn.dev/username/articles/article-id
            article_id_match = re.search(r'/articles/([^/]+)$', url)
            if not article_id_match:
                logger.warning(f"Could not extract article ID from URL: {url}")
                return None

            article_id = article_id_match.group(1)

            # Extract author
            author = creator_elem.text if creator_elem is not None else 'unknown'

            # Extract tags from categories
            categories = item.findall('category')
            tags = [cat.text for cat in categories if cat.text]

            # Get description/content
            description = description_elem.text if description_elem is not None else ''

            # Clean HTML tags from description
            body = re.sub(r'<[^>]+>', '', description)

            return {
                'source': 'zenn',
                'article_id': article_id,
                'title': title,
                'url': url,
                'author': author,
                'author_name': author,
                'author_url': f"https://zenn.dev/{author}",
                'published_at': published_at,
                'updated_at': published_at,
                'likes_count': 0,  # Not available in RSS
                'stocks_count': 0,  # Not available in RSS
                'tags': tags if tags else ['Zenn'],
                'body': body,
                'rendered_body': description,
            }

        except Exception as e:
            logger.error(f"Error parsing RSS item: {e}")
            return None

    def fetch_topic_articles(
        self,
        topic: str,
        days_back: int = 7,
        max_articles: int = 20
    ) -> List[Dict]:
        """
        Fetch articles from a specific Zenn topic

        Args:
            topic: Topic name (e.g., 'python', 'react')
            days_back: Number of days to look back
            max_articles: Maximum number of articles

        Returns:
            List of article dictionaries
        """
        topic_url = f"https://zenn.dev/topics/{topic}/feed"
        logger.info(f"Fetching articles from Zenn topic: {topic}")

        try:
            response = requests.get(topic_url, timeout=30)
            response.raise_for_status()

            root = ET.fromstring(response.content)
            articles = []
            date_threshold = datetime.now() - timedelta(days=days_back)

            for item in root.findall('.//item')[:max_articles]:
                article = self._parse_rss_item(item)
                if article and article['published_at'] >= date_threshold:
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from topic '{topic}'")
            return articles

        except Exception as e:
            logger.error(f"Error fetching topic '{topic}': {e}")
            return []
