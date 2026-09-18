"""
Scraping module using Scrapling library.
Implements fetcher → spider → parser → validator → normalizer → storage pipeline.
"""
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger
import httpx


@dataclass
class ScrapingResult:
    """Result from a scraping operation."""
    source: str
    url: str
    external_id: Optional[str]
    content: str
    content_hash: str
    status: str  # pending, success, failed, duplicate
    error: Optional[str] = None
    scraped_at: datetime = None

    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.utcnow()
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()


class BaseFetcher:
    """Base HTTP fetcher with retry and timeout support."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    async def fetch(self, url: str, headers: Dict = None) -> Optional[str]:
        """Fetch URL content with retries."""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers=headers or {})
                    response.raise_for_status()
                    return response.text
            except Exception as e:
                logger.warning(f"Fetch attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"All fetch attempts failed for {url}")
                    return None
        return None


class BaseSpider:
    """Base spider that defines how to navigate and extract data from a source."""

    def __init__(self, fetcher: BaseFetcher = None):
        self.fetcher = fetcher or BaseFetcher()

    async def run(self) -> List[ScrapingResult]:
        """Execute the spider and return raw results."""
        raise NotImplementedError("Subclasses must implement run()")

    async def _fetch_and_store(self, url: str, source: str, external_id: str = None) -> Optional[ScrapingResult]:
        """Fetch a URL and create a ScrapingResult."""
        content = await self.fetcher.fetch(url)
        if not content:
            return ScrapingResult(
                source=source, url=url, external_id=external_id,
                content="", content_hash="", status="failed",
                error="Failed to fetch content"
            )

        content_hash = hashlib.sha256(content.encode()).hexdigest()

        return ScrapingResult(
            source=source, url=url, external_id=external_id,
            content=content, content_hash=content_hash, status="success"
        )


class BaseParser:
    """Base parser for extracting structured data from raw content."""

    def parse(self, raw_content: str, source: str) -> Dict[str, Any]:
        """Parse raw HTML/text into structured data."""
        raise NotImplementedError("Subclasses must implement parse()")


class BaseNormalizer:
    """
    Normalizer for entity names and data.
    Handles aliases, fuzzy matching, and deduplication.
    """

    def __init__(self):
        self.aliases: Dict[str, str] = {}

    def normalize_name(self, name: str) -> str:
        """Normalize entity name: lowercase, strip, remove common suffixes."""
        if not name:
            return ""
        normalized = name.lower().strip()
        # Remove common suffixes
        for suffix in [" fc", " cf", " club", " team", " united", " city"]:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        # Normalize whitespace
        normalized = " ".join(normalized.split())
        return normalized

    def check_alias(self, name: str) -> Optional[str]:
        """Check if a name matches a known alias."""
        normalized = self.normalize_name(name)
        return self.aliases.get(normalized)

    def add_alias(self, alias: str, canonical: str):
        """Register an alias mapping."""
        self.aliases[self.normalize_name(alias)] = canonical

    def fuzzy_match(self, name: str, candidates: List[str], threshold: float = 0.8) -> Optional[str]:
        """
        Simple fuzzy matching using character overlap.
        Returns the best match above threshold, or None.
        """
        normalized = self.normalize_name(name)
        if not normalized:
            return None

        best_match = None
        best_score = 0.0

        for candidate in candidates:
            norm_candidate = self.normalize_name(candidate)
            score = self._similarity(normalized, norm_candidate)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = candidate

        if best_match and best_score < 0.95:
            logger.info(f"Fuzzy match: '{name}' -> '{best_match}' (score: {best_score:.2f}) - NEEDS_REVIEW")

        return best_match

    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings."""
        if not s1 or not s2:
            return 0.0
        # Simple Jaccard similarity on character bigrams
        def bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1)) if len(s) > 1 else {s}
        b1, b2 = bigrams(s1), bigrams(s2)
        if not b1 or not b2:
            return 0.0
        return len(b1 & b2) / len(b1 | b2)


class ScrapingPipeline:
    """
    Main scraping pipeline that orchestrates the full flow:
    Fetch → Parse → Validate → Normalize → Store
    """

    def __init__(self, spider: BaseSpider, parser: BaseParser, normalizer: BaseNormalizer):
        self.spider = spider
        self.parser = parser
        self.normalizer = normalizer
        self.processed_hashes: set = set()  # Deduplication

    async def run(self) -> List[Dict]:
        """Execute the full pipeline."""
        logger.info("Starting scraping pipeline")

        # Step 1: Fetch raw data
        raw_results = await self.spider.run()
        logger.info(f"Fetched {len(raw_results)} items")

        processed = []
        for result in raw_results:
            # Step 2: Deduplication check
            if result.content_hash in self.processed_hashes:
                logger.debug(f"Duplicate content detected: {result.url}")
                result.status = "duplicate"
                continue

            if result.status != "success":
                logger.warning(f"Skipping failed result: {result.url}")
                continue

            self.processed_hashes.add(result.content_hash)

            # Step 3: Parse
            try:
                parsed = self.parser.parse(result.content, result.source)
            except Exception as e:
                logger.error(f"Parse error for {result.url}: {e}")
                result.status = "failed"
                result.error = str(e)
                continue

            # Step 4: Validate
            if not self._validate(parsed):
                logger.warning(f"Validation failed for {result.url}")
                result.status = "failed"
                result.error = "Validation failed"
                continue

            # Step 5: Normalize
            normalized = self._normalize_data(parsed)

            # Step 6: Store (return for now)
            normalized["_source"] = result.source
            normalized["_url"] = result.url
            normalized["_external_id"] = result.external_id
            normalized["_scraped_at"] = result.scraped_at.isoformat()
            processed.append(normalized)

        logger.info(f"Pipeline complete. Processed: {len(processed)} items")
        return processed

    def _validate(self, data: Dict) -> bool:
        """Validate parsed data structure."""
        if not data:
            return False
        return True

    def _normalize_data(self, data: Dict) -> Dict:
        """Normalize entity names in parsed data."""
        if "home_team" in data:
            data["home_team_normalized"] = self.normalizer.normalize_name(data["home_team"])
        if "away_team" in data:
            data["away_team_normalized"] = self.normalizer.normalize_name(data["away_team"])
        if "referee" in data:
            data["referee_normalized"] = self.normalizer.normalize_name(data["referee"])
        return data
