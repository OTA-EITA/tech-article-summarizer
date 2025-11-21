"""
Path builder for category-based directory structure
Manages article file paths based on category and date
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ArticlePathBuilder:
    """Builds file paths for categorized articles"""

    def __init__(self, base_dir: str = "articles"):
        """
        Initialize path builder

        Args:
            base_dir: Base directory for articles
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def get_article_path(
        self,
        category: str,
        subcategory: str,
        date: datetime,
        create_dirs: bool = True
    ) -> Path:
        """
        Get path for an article file

        Structure: articles/{category}/{subcategory}/{YYYY-MM}/{YYYY-MM-DD}.md

        Args:
            category: Main category
            subcategory: Subcategory
            date: Publication date
            create_dirs: Whether to create directories if they don't exist

        Returns:
            Path object for the article file
        """
        year_month = date.strftime("%Y-%m")
        filename = date.strftime("%Y-%m-%d.md")

        path = self.base_dir / category / subcategory / year_month / filename

        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)

        return path

    def get_category_dir(
        self,
        category: str,
        subcategory: Optional[str] = None
    ) -> Path:
        """
        Get directory path for a category

        Args:
            category: Main category
            subcategory: Optional subcategory

        Returns:
            Path object for the category directory
        """
        if subcategory:
            return self.base_dir / category / subcategory
        else:
            return self.base_dir / category

    def get_category_readme_path(
        self,
        category: str,
        subcategory: Optional[str] = None
    ) -> Path:
        """
        Get path for category README file

        Args:
            category: Main category
            subcategory: Optional subcategory

        Returns:
            Path object for README.md
        """
        category_dir = self.get_category_dir(category, subcategory)
        return category_dir / "README.md"

    def ensure_category_structure(self, category: str, subcategory: str):
        """
        Ensure category directory structure exists

        Args:
            category: Main category
            subcategory: Subcategory
        """
        category_dir = self.get_category_dir(category, subcategory)
        category_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {category_dir}")

    def list_category_months(
        self,
        category: str,
        subcategory: str
    ) -> list:
        """
        List all month directories in a category

        Args:
            category: Main category
            subcategory: Subcategory

        Returns:
            List of (year-month, path) tuples
        """
        category_dir = self.get_category_dir(category, subcategory)

        if not category_dir.exists():
            return []

        months = []
        for month_dir in sorted(category_dir.iterdir()):
            if month_dir.is_dir() and month_dir.name.match(r'\d{4}-\d{2}'):
                months.append((month_dir.name, month_dir))

        return months

    def list_articles_in_month(
        self,
        category: str,
        subcategory: str,
        year_month: str
    ) -> list:
        """
        List all article files in a specific month

        Args:
            category: Main category
            subcategory: Subcategory
            year_month: Year-month string (e.g., "2025-11")

        Returns:
            List of Path objects
        """
        month_dir = self.base_dir / category / subcategory / year_month

        if not month_dir.exists():
            return []

        return sorted(month_dir.glob("*.md"))

    def get_relative_path(self, full_path: Path) -> str:
        """
        Get relative path from base directory

        Args:
            full_path: Full path object

        Returns:
            Relative path string
        """
        try:
            return str(full_path.relative_to(self.base_dir.parent))
        except ValueError:
            return str(full_path)
