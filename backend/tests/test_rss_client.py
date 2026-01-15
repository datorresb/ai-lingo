"""Tests for RSS client module.

Tests cover RSS feed fetching, parsing, caching, error handling,
and the Topic model integration.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.core.rss_client import (
    RSSClient,
    RSSCache,
    CacheEntry,
    list_topics,
    get_topics_from_source,
    get_article_snippet,
    FEED_CONFIG,
)
from src.core.models import Topic


# ============================================================================
# Cache Tests
# ============================================================================


class TestCacheEntry:
    """Tests for CacheEntry class."""

    def test_cache_entry_creation(self) -> None:
        """Test creating a cache entry."""
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        entry = CacheEntry(data, ttl=300)
        assert entry.data == data
        assert entry.ttl == 300
        assert isinstance(entry.timestamp, float)

    def test_cache_entry_not_expired(self) -> None:
        """Test that fresh cache entry is not expired."""
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        entry = CacheEntry(data, ttl=300)
        assert not entry.is_expired()

    def test_cache_entry_expired(self) -> None:
        """Test that old cache entry is expired."""
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        entry = CacheEntry(data, ttl=1)
        time.sleep(1.1)
        assert entry.is_expired()


class TestRSSCache:
    """Tests for RSSCache class."""

    def test_cache_initialization(self) -> None:
        """Test cache initialization."""
        cache = RSSCache(ttl=300)
        assert cache._ttl == 300
        assert len(cache._cache) == 0

    def test_cache_set_and_get(self) -> None:
        """Test setting and getting values from cache."""
        cache = RSSCache(ttl=300)
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        cache.set("test_key", data)
        retrieved = cache.get("test_key")
        assert retrieved == data

    def test_cache_get_nonexistent(self) -> None:
        """Test getting nonexistent key returns None."""
        cache = RSSCache(ttl=300)
        assert cache.get("nonexistent") is None

    def test_cache_get_expired(self) -> None:
        """Test that expired cache returns None and cleans up."""
        cache = RSSCache(ttl=1)
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        cache.set("test_key", data)
        time.sleep(1.1)
        assert cache.get("test_key") is None
        assert "test_key" not in cache._cache

    def test_cache_clear(self) -> None:
        """Test clearing the cache."""
        cache = RSSCache(ttl=300)
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        cache.set("key1", data)
        cache.set("key2", data)
        assert len(cache._cache) == 2
        cache.clear()
        assert len(cache._cache) == 0

    def test_cache_get_stats(self) -> None:
        """Test cache statistics."""
        cache = RSSCache(ttl=300)
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        cache.set("key1", data)
        cache.set("key2", data)
        stats = cache.get_stats()
        assert stats["total_entries"] == 2
        assert stats["expired_entries"] == 0

    def test_cache_get_stats_with_expired(self) -> None:
        """Test cache statistics with expired entries."""
        cache = RSSCache(ttl=1)
        data = [Topic(headline="Test", source="BBC", url="http://example.com")]
        cache.set("key1", data)
        time.sleep(1.1)
        stats = cache.get_stats()
        assert stats["total_entries"] == 1
        assert stats["expired_entries"] == 1


# ============================================================================
# RSS Client Tests
# ============================================================================


class TestRSSClient:
    """Tests for RSSClient class."""

    def test_client_initialization(self) -> None:
        """Test client initialization with defaults."""
        client = RSSClient()
        assert isinstance(client.cache, RSSCache)
        assert client.feeds == FEED_CONFIG

    def test_client_custom_feeds(self) -> None:
        """Test client initialization with custom feeds."""
        custom_feeds = {"Custom": "http://example.com/feed"}
        client = RSSClient(feeds=custom_feeds)
        assert client.feeds == custom_feeds

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_success(self, mock_parse: Mock) -> None:
        """Test successfully fetching topics from RSS feed."""
        # Mock feed data
        mock_feed = {
            "feed": {"title": "BBC News"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
                {"title": "Headline 2", "link": "http://example.com/2"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.list_topics("http://feeds.bbc.co.uk/news/rss.xml", limit=10)

        assert len(topics) == 2
        assert topics[0].headline == "Headline 1"
        assert topics[0].source == "BBC News"
        assert topics[0].url == "http://example.com/1"

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_caching(self, mock_parse: Mock) -> None:
        """Test that topics are cached on subsequent requests."""
        mock_feed = {
            "feed": {"title": "BBC News"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient(cache_ttl=300)
        url = "http://feeds.bbc.co.uk/news/rss.xml"

        # First call
        topics1 = client.list_topics(url)
        call_count_1 = mock_parse.call_count

        # Second call (should use cache)
        topics2 = client.list_topics(url)
        call_count_2 = mock_parse.call_count

        assert topics1 == topics2
        assert call_count_2 == call_count_1  # No additional calls

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_limit(self, mock_parse: Mock) -> None:
        """Test that limit parameter works correctly."""
        mock_feed = {
            "feed": {"title": "BBC News"},
            "entries": [
                {"title": f"Headline {i}", "link": f"http://example.com/{i}"}
                for i in range(10)
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.list_topics("http://feeds.bbc.co.uk/news/rss.xml", limit=5)

        assert len(topics) == 5

    def test_list_topics_empty_url(self) -> None:
        """Test that empty URL raises ValueError."""
        client = RSSClient()
        with pytest.raises(ValueError, match="Feed URL cannot be empty"):
            client.list_topics("")

    def test_list_topics_invalid_limit(self) -> None:
        """Test that invalid limit raises ValueError."""
        client = RSSClient()
        with pytest.raises(ValueError, match="Limit must be at least 1"):
            client.list_topics("http://example.com/feed", limit=0)

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_network_error(self, mock_parse: Mock) -> None:
        """Test handling of network errors."""
        mock_parse.side_effect = Exception("Network error")

        client = RSSClient()
        with pytest.raises(Exception, match="Failed to fetch RSS feed"):
            client.list_topics("http://invalid-feed.com/rss")

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_invalid_entries(self, mock_parse: Mock) -> None:
        """Test filtering of invalid entries (missing title or link)."""
        mock_feed = {
            "feed": {"title": "Test Feed"},
            "entries": [
                {"title": "Valid Headline", "link": "http://example.com/1"},
                {"title": "", "link": "http://example.com/2"},  # Missing title
                {"title": "No Link", "link": ""},  # Missing link
                {"link": "http://example.com/3"},  # Missing title
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.list_topics("http://example.com/feed")

        assert len(topics) == 1
        assert topics[0].headline == "Valid Headline"

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_bozo_feed(self, mock_parse: Mock) -> None:
        """Test handling of malformed feeds (bozo flag set)."""
        mock_feed = {
            "feed": {"title": "Malformed Feed"},
            "entries": [
                {"title": "Headline", "link": "http://example.com/1"},
            ],
            "bozo": True,  # Feed has parsing issues
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.list_topics("http://example.com/feed")

        # Should still return valid entries despite bozo flag
        assert len(topics) == 1

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_extract_source_from_url(self, mock_parse: Mock) -> None:
        """Test extracting source name from feed URL when feed title is missing."""
        mock_feed = {
            "feed": {},  # No title in feed
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.list_topics(FEED_CONFIG["BBC"], limit=10)

        assert len(topics) == 1
        assert topics[0].source == "BBC"

    def test_get_article_snippet(self) -> None:
        """Test get_article_snippet returns None for basic implementation."""
        client = RSSClient()
        snippet = client.get_article_snippet("http://example.com/article")
        assert snippet is None

    def test_get_article_snippet_empty_url(self) -> None:
        """Test get_article_snippet with empty URL."""
        client = RSSClient()
        snippet = client.get_article_snippet("")
        assert snippet is None

    @patch("src.core.rss_client.feedparser.parse")
    def test_get_topics_from_source(self, mock_parse: Mock) -> None:
        """Test fetching topics from a named source."""
        mock_feed = {
            "feed": {"title": "BBC News"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.get_topics_from_source("BBC", limit=10)

        assert len(topics) == 1
        assert topics[0].source == "BBC News"

    def test_get_topics_from_source_invalid(self) -> None:
        """Test that invalid source raises ValueError."""
        client = RSSClient()
        with pytest.raises(ValueError, match="Source 'Invalid' not configured"):
            client.get_topics_from_source("Invalid")

    @patch("src.core.rss_client.feedparser.parse")
    def test_get_topics_from_multiple_sources(self, mock_parse: Mock) -> None:
        """Test fetching topics from multiple sources."""
        mock_feed = {
            "feed": {"title": "Test Feed"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        results = client.get_topics_from_multiple_sources(
            sources=["BBC", "NYT"], limit_per_source=1
        )

        assert "BBC" in results
        assert "NYT" in results
        assert len(results["BBC"]) == 1
        assert len(results["NYT"]) == 1

    @patch("src.core.rss_client.feedparser.parse")
    def test_get_topics_from_multiple_sources_all(self, mock_parse: Mock) -> None:
        """Test fetching from all configured sources when none specified."""
        mock_feed = {
            "feed": {"title": "Test Feed"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        results = client.get_topics_from_multiple_sources(limit_per_source=1)

        # Should include all configured sources
        assert "BBC" in results
        assert "NYT" in results
        assert "TechCrunch" in results

    @patch("src.core.rss_client.feedparser.parse")
    def test_get_topics_from_multiple_sources_error_handling(
        self, mock_parse: Mock
    ) -> None:
        """Test that errors in one source don't affect others."""
        def parse_side_effect(url):
            if "bbc" in url:
                raise Exception("BBC feed unavailable")
            return {
                "feed": {"title": "Test Feed"},
                "entries": [
                    {"title": "Headline 1", "link": "http://example.com/1"},
                ],
                "bozo": False,
            }

        mock_parse.side_effect = parse_side_effect

        client = RSSClient()
        results = client.get_topics_from_multiple_sources(
            sources=["BBC", "NYT"], limit_per_source=1
        )

        # BBC should have empty list due to error
        assert results["BBC"] == []
        # NYT should have valid topics
        assert len(results["NYT"]) == 1

    def test_clear_cache(self) -> None:
        """Test clearing the cache."""
        client = RSSClient()
        # Add something to cache
        client.cache.set("key", [])
        assert len(client.cache._cache) > 0
        
        client.clear_cache()
        assert len(client.cache._cache) == 0

    def test_get_cache_stats(self) -> None:
        """Test getting cache statistics."""
        client = RSSClient()
        stats = client.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert "total_entries" in stats
        assert "expired_entries" in stats

    @staticmethod
    def test_extract_source_from_url() -> None:
        """Test extracting source from feed URL."""
        assert RSSClient._extract_source_from_url(FEED_CONFIG["BBC"]) == "BBC"
        assert RSSClient._extract_source_from_url(FEED_CONFIG["NYT"]) == "NYT"
        assert RSSClient._extract_source_from_url(FEED_CONFIG["TechCrunch"]) == "TechCrunch"
        assert RSSClient._extract_source_from_url("http://unknown.com/feed") == "Unknown"


# ============================================================================
# Module-level Function Tests
# ============================================================================


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    @patch("src.core.rss_client.feedparser.parse")
    def test_list_topics_function(self, mock_parse: Mock) -> None:
        """Test the module-level list_topics function."""
        mock_feed = {
            "feed": {"title": "Test Feed"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        topics = list_topics("http://example.com/feed", limit=5)
        assert isinstance(topics, list)
        assert len(topics) > 0

    def test_get_article_snippet_function(self) -> None:
        """Test the module-level get_article_snippet function."""
        snippet = get_article_snippet("http://example.com/article")
        assert snippet is None

    @patch("src.core.rss_client.feedparser.parse")
    def test_get_topics_from_source_function(self, mock_parse: Mock) -> None:
        """Test the module-level get_topics_from_source function."""
        mock_feed = {
            "feed": {"title": "BBC News"},
            "entries": [
                {"title": "Headline 1", "link": "http://example.com/1"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        topics = get_topics_from_source("BBC", limit=5)
        assert isinstance(topics, list)


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for RSS client with Topic model."""

    @patch("src.core.rss_client.feedparser.parse")
    def test_rss_to_topic_model_integration(self, mock_parse: Mock) -> None:
        """Test complete workflow from RSS to Topic model."""
        mock_feed = {
            "feed": {"title": "BBC News"},
            "entries": [
                {"title": "AI Reaches New Milestone", "link": "https://bbc.com/news/ai"},
                {"title": "Climate Report Released", "link": "https://bbc.com/news/climate"},
            ],
            "bozo": False,
        }
        mock_parse.return_value = mock_feed

        client = RSSClient()
        topics = client.list_topics(FEED_CONFIG["BBC"], limit=10)

        # Verify all topics are properly formatted Topic instances
        for topic in topics:
            assert isinstance(topic, Topic)
            assert len(topic.headline) > 0
            assert topic.source == "BBC News"
            assert topic.url.startswith("https://")

    @patch("src.core.rss_client.feedparser.parse")
    def test_multiple_feeds_aggregation(self, mock_parse: Mock) -> None:
        """Test aggregating topics from multiple feeds."""
        def parse_side_effect(url):
            if "bbc" in url:
                return {
                    "feed": {"title": "BBC News"},
                    "entries": [
                        {"title": "BBC Story", "link": "http://bbc.com/1"},
                    ],
                    "bozo": False,
                }
            else:
                return {
                    "feed": {"title": "NYT"},
                    "entries": [
                        {"title": "NYT Story", "link": "http://nyt.com/1"},
                    ],
                    "bozo": False,
                }

        mock_parse.side_effect = parse_side_effect

        client = RSSClient()
        bbc_topics = client.get_topics_from_source("BBC", limit=5)
        nyt_topics = client.get_topics_from_source("NYT", limit=5)

        assert len(bbc_topics) > 0
        assert len(nyt_topics) > 0
        assert bbc_topics[0].headline == "BBC Story"
        assert nyt_topics[0].headline == "NYT Story"
