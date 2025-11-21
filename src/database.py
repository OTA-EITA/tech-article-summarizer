"""
SQLite database module for article management
Handles duplicate detection and article tracking
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ArticleDatabase:
    """SQLite database for article tracking and duplicate detection"""

    def __init__(self, db_path: str = "data/articles.db"):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = None
        self.connect()
        self.init_db()

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")

    def init_db(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()

        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                article_id TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT,
                author_name TEXT,
                published_at DATETIME,
                fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,

                file_path TEXT NOT NULL,

                tags TEXT,
                likes_count INTEGER DEFAULT 0,
                stocks_count INTEGER DEFAULT 0,

                is_summarized BOOLEAN DEFAULT 0,

                UNIQUE(source, article_id)
            )
        """)

        # Category stats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL,
                article_count INTEGER DEFAULT 0,
                total_likes INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(category, subcategory)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_published_at
            ON articles(published_at)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category
            ON articles(category, subcategory)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fetched_at
            ON articles(fetched_at)
        """)

        self.conn.commit()
        logger.info("Database schema initialized")

    def article_exists(self, source: str, article_id: str) -> bool:
        """
        Check if article already exists in database

        Args:
            source: Article source (qiita, zenn, etc.)
            article_id: Unique article ID

        Returns:
            True if article exists
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT 1 FROM articles WHERE source = ? AND article_id = ? LIMIT 1",
            (source, article_id)
        )
        return cursor.fetchone() is not None

    def add_article(
        self,
        article: Dict,
        category: str,
        subcategory: str,
        file_path: str
    ) -> int:
        """
        Add new article to database

        Args:
            article: Article dictionary
            category: Main category
            subcategory: Subcategory
            file_path: Path to saved markdown file

        Returns:
            Article ID in database
        """
        cursor = self.conn.cursor()

        tags_json = json.dumps(article.get('tags', []), ensure_ascii=False)

        cursor.execute("""
            INSERT OR REPLACE INTO articles (
                source, article_id, url, title, author, author_name,
                published_at, category, subcategory, file_path,
                tags, likes_count, stocks_count, is_summarized
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article['source'],
            article['article_id'],
            article['url'],
            article['title'],
            article['author'],
            article.get('author_name', article['author']),
            article['published_at'].isoformat() if isinstance(article['published_at'], datetime) else article['published_at'],
            category,
            subcategory,
            file_path,
            tags_json,
            article.get('likes_count', 0),
            article.get('stocks_count', 0),
            1  # is_summarized = True
        ))

        self.conn.commit()
        article_id = cursor.lastrowid

        # Update category stats
        self._update_category_stats(category, subcategory, article.get('likes_count', 0))

        logger.info(f"Added article to database: {article['title']} (ID: {article_id})")
        return article_id

    def _update_category_stats(self, category: str, subcategory: str, likes: int):
        """Update category statistics"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO category_stats (category, subcategory, article_count, total_likes)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(category, subcategory) DO UPDATE SET
                article_count = article_count + 1,
                total_likes = total_likes + ?,
                last_updated = CURRENT_TIMESTAMP
        """, (category, subcategory, likes, likes))

        self.conn.commit()

    def get_articles_by_category(
        self,
        category: str,
        subcategory: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get articles by category

        Args:
            category: Main category
            subcategory: Optional subcategory filter
            limit: Maximum number of articles

        Returns:
            List of article dictionaries
        """
        cursor = self.conn.cursor()

        if subcategory:
            cursor.execute("""
                SELECT * FROM articles
                WHERE category = ? AND subcategory = ?
                ORDER BY published_at DESC
                LIMIT ?
            """, (category, subcategory, limit))
        else:
            cursor.execute("""
                SELECT * FROM articles
                WHERE category = ?
                ORDER BY published_at DESC
                LIMIT ?
            """, (category, limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_all_categories(self) -> List[Tuple[str, str]]:
        """
        Get all unique category/subcategory pairs

        Returns:
            List of (category, subcategory) tuples
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT category, subcategory
            FROM articles
            ORDER BY category, subcategory
        """)
        return cursor.fetchall()

    def get_category_stats(self, category: str, subcategory: str) -> Optional[Dict]:
        """
        Get statistics for a category

        Args:
            category: Main category
            subcategory: Subcategory

        Returns:
            Stats dictionary or None
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM category_stats
            WHERE category = ? AND subcategory = ?
        """, (category, subcategory))

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_recent_articles(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """
        Get recent articles from last N days

        Args:
            days: Number of days to look back
            limit: Maximum number of articles

        Returns:
            List of article dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM articles
            WHERE date(published_at) >= date('now', ? || ' days')
            ORDER BY published_at DESC
            LIMIT ?
        """, (f'-{days}', limit))

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_popular_tags(self, limit: int = 20) -> List[Tuple[str, int]]:
        """
        Get most popular tags

        Args:
            limit: Maximum number of tags

        Returns:
            List of (tag, count) tuples
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT tags FROM articles WHERE tags IS NOT NULL")

        tag_counts = {}
        for row in cursor.fetchall():
            tags = json.loads(row['tags'])
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_tags[:limit]

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
