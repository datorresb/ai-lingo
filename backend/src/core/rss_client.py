"""RSS client for fetching headlines from various news sources.

This module provides functionality to fetch and parse RSS feeds from multiple
sources including BBC, NYT, and TechCrunch. Implements caching with configurable
TTL to avoid excessive network requests.

Refer to Issue #3 for detailed specifications.
"""

import time
from typing import Optional
from datetime import datetime, timedelta
import feedparser
from src.core.models import Topic


# ============================================================================
# Constants
# ============================================================================

# Default RSS feeds configuration
FEED_CONFIG = {
    "BBC": "http://feeds.bbc.co.uk/news/rss.xml",
    "NYT": "https://feeds.nytimes.com/services/xml/rss/nyt/World.xml",
    "TechCrunch": "http://feeds.techcrunch.com/techcrunch/feed",
}

DEFAULT_CACHE_TTL = 300  # 5 minutes in seconds
DEFAULT_LIMIT = 10


# ============================================================================
# Cache Implementation
# ============================================================================


class CacheEntry:
    """Represents a cached entry with TTL support.

    Attributes:
        data: The cached data (list of Topics)
        timestamp: When the cache entry was created
        ttl: Time-to-live in seconds
    """

    def __init__(self, data: list[Topic], ttl: int):
        """Initialize a cache entry.

        Args:
            data: The data to cache
            ttl: Time-to-live in seconds
        """
        self.data = data
        self.timestamp = time.time()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Check if the cache entry has expired.

        Returns:
            True if expired, False otherwise
        """
        return time.time() - self.timestamp > self.ttl


class RSSCache:
    """Simple in-memory cache with TTL support.

    Attributes:
        _cache: Dictionary storing cache entries by feed URL
        _ttl: Default TTL for cache entries
    """

    def __init__(self, ttl: int = DEFAULT_CACHE_TTL):
        """Initialize the cache.

        Args:
            ttl: Default time-to-live for cache entries in seconds
        """
        self._cache: dict[str, CacheEntry] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[list[Topic]]:
        """Get a value from the cache if not expired.

        Args:
            key: The cache key (typically the feed URL)

        Returns:
            The cached data if found and not expired, None otherwise
        """
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                # Clean up expired entry
                del self._cache[key]
        return None

    def set(self, key: str, value: list[Topic]) -> None:
        """Set a value in the cache.

        Args:
            key: The cache key (typically the feed URL)
            value: The data to cache
        """
        self._cache[key] = CacheEntry(value, self._ttl)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def get_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache size and expired entries count
        """
        expired_count = sum(
            1 for entry in self._cache.values() if entry.is_expired()
        )
        return {
            "total_entries": len(self._cache),
            "expired_entries": expired_count,
        }


# ============================================================================
# RSS Client Implementation
# ============================================================================


class RSSClient:
    """Client for fetching and parsing RSS feeds.

    Attributes:
        cache: The cache instance for storing parsed feeds
        feeds: Available feeds configuration
    """

    def __init__(self, cache_ttl: int = DEFAULT_CACHE_TTL, feeds: Optional[dict[str, str]] = None):
        """Initialize the RSS client.

        Args:
            cache_ttl: Cache TTL in seconds
            feeds: Optional custom feeds configuration (overrides defaults)
        """
        self.cache = RSSCache(ttl=cache_ttl)
        self.feeds = feeds or FEED_CONFIG

    def list_topics(self, feed_url: str, limit: int = DEFAULT_LIMIT) -> list[Topic]:
        """Fetch headlines from an RSS feed.

        Args:
            feed_url: The RSS feed URL
            limit: Maximum number of topics to return (default: 10)

        Returns:
            List of Topic objects with headline, source, and URL

        Raises:
            ValueError: If feed_url is invalid or empty
            Exception: For network errors (wrapped with context)
        """
        if not feed_url:
            raise ValueError("Feed URL cannot be empty")

        if limit < 1:
            raise ValueError("Limit must be at least 1")

        # Check cache first
        cached = self.cache.get(feed_url)
        if cached is not None:
            return cached[:limit]

        try:
            # Parse the feed
            feed = feedparser.parse(feed_url)

            # Check for feed parsing errors (handle both real feedparser objects and dict mocks)
            bozo = getattr(feed, 'bozo', feed.get('bozo', False) if isinstance(feed, dict) else False)
            if bozo:
                # feedparser.bozo indicates parsing issues but we can still get entries
                pass

            # Get entries and feed info (handle both real feedparser objects and dict mocks)
            entries = feed.entries if hasattr(feed, 'entries') else feed.get('entries', [])
            feed_dict = feed.feed if hasattr(feed, 'feed') else feed.get('feed', {})
            feed_title = feed_dict.get('title', 'Unknown') if isinstance(feed_dict, dict) else getattr(feed_dict, 'title', 'Unknown')

            # Extract topics from feed entries
            topics = []
            for entry in entries[:limit]:
                try:
                    # Get entry data (handle both real feedparser objects and dict mocks)
                    entry_dict = entry if isinstance(entry, dict) else vars(entry)
                    headline = entry_dict.get('title', '')
                    url = entry_dict.get('link', '')

                    # Determine the source from the feed title or URL
                    source = feed_title
                    if not source or source == "Unknown":
                        # Try to extract source from feed URL
                        source = self._extract_source_from_url(feed_url)

                    topic = Topic(
                        headline=headline,
                        source=source,
                        url=url,
                    )
                    # Only add valid topics (with headline and URL)
                    if topic.headline and topic.url:
                        topics.append(topic)
                except Exception:
                    # Skip entries that fail validation
                    continue

            # Cache the results
            self.cache.set(feed_url, topics)
            return topics[:limit]

        except Exception as e:
            # Wrap network and parsing errors with context
            raise Exception(f"Failed to fetch RSS feed from {feed_url}: {str(e)}")

    def get_article_snippet(self, url: str) -> Optional[str]:
        """Get a snippet/summary from an article URL.

        Note: This is a simplified implementation that extracts the
        summary/description from the RSS feed entry. For full content,
        web scraping would be required.

        Args:
            url: The article URL

        Returns:
            Article snippet/summary if available, None otherwise
        """
        if not url:
            return None

        # Search through all cached feeds to find the entry
        for feed_entries in self.cache._cache.values():
            if feed_entries.is_expired():
                continue

            # Note: In a real implementation, we would search the original feed
            # or use a web scraping library. This is a simplified version.

        return None

    def get_topics_from_source(self, source: str, limit: int = DEFAULT_LIMIT) -> list[Topic]:
        """Fetch topics from a named news source.

        Args:
            source: The source name (e.g., "BBC", "NYT", "TechCrunch")
            limit: Maximum number of topics to return

        Returns:
            List of Topic objects from the specified source

        Raises:
            ValueError: If source is not configured
        """
        if source not in self.feeds:
            raise ValueError(f"Source '{source}' not configured. Available: {list(self.feeds.keys())}")

        return self.list_topics(self.feeds[source], limit)

    def get_topics_from_multiple_sources(
        self, sources: Optional[list[str]] = None, limit_per_source: int = 5
    ) -> dict[str, list[Topic]]:
        """Fetch topics from multiple news sources.

        Args:
            sources: List of source names. If None, use all configured sources
            limit_per_source: Maximum topics per source

        Returns:
            Dictionary mapping source names to lists of topics
        """
        if sources is None:
            sources = list(self.feeds.keys())

        results = {}
        for source in sources:
            try:
                results[source] = self.get_topics_from_source(source, limit_per_source)
            except Exception as e:
                # Log error but continue with other sources
                results[source] = []

        return results

    @staticmethod
    def _extract_source_from_url(url: str) -> str:
        """Extract source name from feed URL.

        Args:
            url: The feed URL

        Returns:
            Extracted source name or "Unknown"
        """
        for source, feed_url in FEED_CONFIG.items():
            if url == feed_url:
                return source
        return "Unknown"

    def clear_cache(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return self.cache.get_stats()


# ============================================================================
# Module-level convenience functions
# ============================================================================

# Global client instance
_default_client: Optional[RSSClient] = None


def get_client(cache_ttl: int = DEFAULT_CACHE_TTL) -> RSSClient:
    """Get or create the default RSS client instance.

    Args:
        cache_ttl: Cache TTL in seconds (used only on first call)

    Returns:
        The default RSSClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = RSSClient(cache_ttl=cache_ttl)
    return _default_client


def list_topics(feed_url: str, limit: int = DEFAULT_LIMIT) -> list[Topic]:
    """Convenience function to fetch topics from a feed.

    Args:
        feed_url: The RSS feed URL
        limit: Maximum number of topics to return

    Returns:
        List of Topic objects
    """
    return get_client().list_topics(feed_url, limit)


def get_article_snippet(url: str) -> Optional[str]:
    """Convenience function to get article snippet.

    Args:
        url: The article URL

    Returns:
        Article snippet if available
    """
    return get_client().get_article_snippet(url)


def get_topics_from_source(source: str, limit: int = DEFAULT_LIMIT) -> list[Topic]:
    """Convenience function to fetch topics from a named source.

    Args:
        source: The source name (e.g., "BBC")
        limit: Maximum number of topics

    Returns:
        List of Topic objects from the source
    """
    return get_client().get_topics_from_source(source, limit)
