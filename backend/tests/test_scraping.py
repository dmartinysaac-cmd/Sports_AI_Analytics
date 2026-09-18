"""
Tests for the scraping pipeline and normalizer.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.scraping.pipeline import BaseNormalizer, ScrapingResult


class TestNormalizer:
    """Tests for entity name normalization."""

    def setup_method(self):
        self.normalizer = BaseNormalizer()

    def test_lowercase(self):
        assert self.normalizer.normalize_name("Manchester City") == "manchester city"

    def test_strip_whitespace(self):
        assert self.normalizer.normalize_name("  Arsenal FC  ") == "arsenal"

    def test_remove_fc_suffix(self):
        assert self.normalizer.normalize_name("Barcelona FC") == "barcelona"

    def test_remove_cf_suffix(self):
        assert self.normalizer.normalize_name("Real Madrid CF") == "real madrid"

    def test_normalize_spaces(self):
        assert self.normalizer.normalize_name("Bayern   Munich") == "bayern munich"

    def test_empty_string(self):
        assert self.normalizer.normalize_name("") == ""
        assert self.normalizer.normalize_name(None) == ""

    def test_alias_lookup(self):
        self.normalizer.add_alias("Man City", "Manchester City")
        assert self.normalizer.check_alias("Man City") == "Manchester City"
        assert self.normalizer.check_alias("man city") == "Manchester City"

    def test_alias_not_found(self):
        assert self.normalizer.check_alias("Unknown Team") is None

    def test_fuzzy_match_exact(self):
        candidates = ["Manchester City", "Arsenal", "Liverpool"]
        result = self.normalizer.fuzzy_match("Manchester City", candidates, threshold=0.9)
        assert result == "Manchester City"

    def test_fuzzy_match_close(self):
        candidates = ["Manchester City", "Arsenal", "Liverpool"]
        result = self.normalizer.fuzzy_match("Manchester Cit", candidates, threshold=0.8)
        assert result == "Manchester City"

    def test_fuzzy_match_no_match(self):
        candidates = ["Manchester City", "Arsenal", "Liverpool"]
        result = self.normalizer.fuzzy_match("Totally Different", candidates, threshold=0.8)
        assert result is None


class TestScrapingResult:
    """Tests for ScrapingResult data class."""

    def test_auto_hash(self):
        result = ScrapingResult(
            source="test", url="http://test.com",
            external_id="123", content="<html>test</html>",
            content_hash="", status="success"
        )
        assert result.content_hash != ""
        assert len(result.content_hash) == 64  # SHA256

    def test_auto_timestamp(self):
        result = ScrapingResult(
            source="test", url="http://test.com",
            external_id="123", content="test",
            content_hash="abc", status="success"
        )
        assert result.scraped_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
