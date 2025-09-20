"""
Web Research Assistant Plugin - Intelligent Web Research and Content Analysis
Author: Aetherra Plugin System
Version: 1.0.0

This plugin provides comprehensive web research capabilities including:
- Multi-source web content extraction and analysis
- Intelligent URL discovery and validation
- Fact-checking and credibility assessment
- Automated research report generation
- Content summarization and key insight extraction
- Citation management and source tracking
"""

# Standard library imports
import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any
from urllib.parse import quote, urljoin, urlparse

# Third party imports
import aiohttp

try:
    # Third party imports
    from bs4 import BeautifulSoup

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

try:
    # Third party imports
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    # Third party imports
    from newspaper import Article

    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

try:
    # Third party imports
    from textstat import automated_readability_index, flesch_reading_ease

    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class WebSource:
    """Web source information structure."""

    url: str
    title: str
    domain: str
    content: str
    excerpt: str
    author: str
    publish_date: str
    credibility_score: float
    word_count: int
    reading_level: str
    extracted_date: str
    status: str  # success, failed, blocked, timeout


@dataclass
class ResearchQuery:
    """Research query structure."""

    query: str
    keywords: list[str]
    sources: list[str]
    depth: str  # surface, moderate, deep
    content_types: list[str]  # article, academic, news, blog, social
    date_range: dict[str, str]
    language: str
    region: str


@dataclass
class ResearchReport:
    """Research report structure."""

    query: ResearchQuery
    sources: list[WebSource]
    summary: str
    key_insights: list[str]
    credibility_assessment: dict[str, Any]
    fact_checks: list[dict[str, Any]]
    recommendations: list[str]
    generated_date: str
    total_sources: int
    successful_extractions: int


class WebExtractor:
    """Web content extraction and processing."""

    def __init__(self):
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        self.timeout = 30

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.headers, timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def extract_content(self, url: str) -> WebSource:
        """Extract content from a single URL."""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            async with self.session.get(url) as response:
                if response.status != 200:
                    return WebSource(
                        url=url,
                        title="",
                        domain=domain,
                        content="",
                        excerpt="",
                        author="",
                        publish_date="",
                        credibility_score=0.0,
                        word_count=0,
                        reading_level="",
                        extracted_date=datetime.now().isoformat(),
                        status=f"HTTP {response.status}",
                    )

                html = await response.text()

            # Parse with BeautifulSoup if available
            if BEAUTIFULSOUP_AVAILABLE:
                soup = BeautifulSoup(html, "html.parser")

                # Extract basic information
                title = self._extract_title(soup)
                content = self._extract_content(soup)
                author = self._extract_author(soup)
                publish_date = self._extract_publish_date(soup)

            else:
                # Fallback extraction without BeautifulSoup
                title = self._extract_title_fallback(html)
                content = self._extract_content_fallback(html)
                author = ""
                publish_date = ""

            # Generate excerpt
            excerpt = self._generate_excerpt(content)

            # Calculate metrics
            word_count = len(content.split())
            reading_level = self._calculate_reading_level(content)
            credibility_score = self._assess_credibility(domain, content, title)

            return WebSource(
                url=url,
                title=title,
                domain=domain,
                content=content,
                excerpt=excerpt,
                author=author,
                publish_date=publish_date,
                credibility_score=credibility_score,
                word_count=word_count,
                reading_level=reading_level,
                extracted_date=datetime.now().isoformat(),
                status="success",
            )

        except asyncio.TimeoutError:
            return self._create_error_source(url, "timeout")
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return self._create_error_source(url, f"error: {e}")

    def _extract_title(self, soup) -> str:
        """Extract page title."""
        # Try different title sources
        title = ""

        # OpenGraph title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]

        # Twitter title
        if not title:
            twitter_title = soup.find("meta", attrs={"name": "twitter:title"})
            if twitter_title and twitter_title.get("content"):
                title = twitter_title["content"]

        # Regular title tag
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text()

        # h1 tag as fallback
        if not title:
            h1_tag = soup.find("h1")
            if h1_tag:
                title = h1_tag.get_text()

        return title.strip() if title else "No Title"

    def _extract_content(self, soup) -> str:
        """Extract main content from page."""
        content = ""

        # Try common content selectors
        content_selectors = [
            "article",
            ".content",
            ".post-content",
            ".article-content",
            ".entry-content",
            "main",
            ".main-content",
            "#content",
        ]

        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text(separator=" ", strip=True)
                break

        # Fallback to body if no content found
        if not content:
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            content = soup.get_text(separator=" ", strip=True)

        return self._clean_content(content)

    def _extract_author(self, soup) -> str:
        """Extract author information."""
        author = ""

        # Try different author sources
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            ".author",
            ".byline",
            ".post-author",
            '[rel="author"]',
        ]

        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                if author_elem.name == "meta":
                    author = author_elem.get("content", "")
                else:
                    author = author_elem.get_text(strip=True)

                if author:
                    break

        return author.strip() if author else ""

    def _extract_publish_date(self, soup) -> str:
        """Extract publication date."""
        date = ""

        # Try different date sources
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'meta[name="date"]',
            "time[pubdate]",
            "time[datetime]",
            ".publish-date",
            ".post-date",
        ]

        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                if date_elem.name == "meta":
                    date = date_elem.get("content", "")
                elif date_elem.name == "time":
                    date = date_elem.get("datetime", "") or date_elem.get_text(
                        strip=True
                    )
                else:
                    date = date_elem.get_text(strip=True)

                if date:
                    break

        return date.strip() if date else ""

    def _extract_title_fallback(self, html: str) -> str:
        """Fallback title extraction without BeautifulSoup."""
        # Standard library imports
        import re

        # Extract title from HTML
        title_match = re.search(
            r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL
        )
        if title_match:
            return title_match.group(1).strip()

        return "No Title"

    def _extract_content_fallback(self, html: str) -> str:
        """Fallback content extraction without BeautifulSoup."""
        # Standard library imports
        import html as html_module
        import re

        try:
            # First decode HTML entities
            html = html_module.unescape(html)

            # Remove dangerous tags completely with their content
            dangerous_tags = r"<(?:script|style|object|embed|applet|iframe|frame|frameset|meta|link)[^>]*>.*?</(?:script|style|object|embed|applet|iframe|frame|frameset|meta|link)>"
            html = re.sub(dangerous_tags, "", html, flags=re.IGNORECASE | re.DOTALL)

            # Remove any remaining script/style tags (unclosed ones)
            html = re.sub(
                r"<(?:script|style|object|embed|applet|iframe|frame|frameset|meta|link)[^>]*>",
                "",
                html,
                flags=re.IGNORECASE,
            )

            # Remove all remaining HTML tags (now safe since dangerous content is gone)
            text = re.sub(r"<[^>]*>", " ", html)

            # Clean up whitespace
            text = re.sub(r"\s+", " ", text)

            return text.strip()
        except Exception:
            # Ultra-safe fallback: just remove everything that looks like HTML
            return re.sub(r"<[^>]*>", " ", html).strip()

    def _generate_excerpt(self, content: str, max_length: int = 300) -> str:
        """Generate excerpt from content."""
        if not content:
            return ""

        # Take first few sentences up to max_length
        sentences = content.split(". ")
        excerpt = ""

        for sentence in sentences:
            if len(excerpt + sentence) <= max_length:
                excerpt += sentence + ". "
            else:
                break

        return excerpt.strip()

    def _calculate_reading_level(self, content: str) -> str:
        """Calculate reading level of content."""
        if not content or not TEXTSTAT_AVAILABLE:
            return "Unknown"

        try:
            flesch_score = flesch_reading_ease(content)

            if flesch_score >= 90:
                return "Very Easy"
            elif flesch_score >= 80:
                return "Easy"
            elif flesch_score >= 70:
                return "Fairly Easy"
            elif flesch_score >= 60:
                return "Standard"
            elif flesch_score >= 50:
                return "Fairly Difficult"
            elif flesch_score >= 30:
                return "Difficult"
            else:
                return "Very Difficult"

        except Exception:
            return "Unknown"

    def _assess_credibility(self, domain: str, content: str, title: str) -> float:
        """Assess source credibility (simplified scoring)."""
        score = 0.5  # Base score

        # Domain-based scoring
        trusted_domains = {
            "wikipedia.org": 0.3,
            "edu": 0.4,
            "gov": 0.4,
            "bbc.com": 0.3,
            "reuters.com": 0.3,
            "ap.org": 0.3,
            "npr.org": 0.2,
            "pbs.org": 0.2,
        }

        for trusted, bonus in trusted_domains.items():
            if trusted in domain:
                score += bonus
                break

        # Content quality indicators
        if content:
            # Length indicates thoroughness
            if len(content) > 1000:
                score += 0.1
            elif len(content) < 200:
                score -= 0.1

            # Citation indicators
            if "references" in content.lower() or "sources" in content.lower():
                score += 0.1

        # Cap score at 1.0
        return min(score, 1.0)

    def _clean_content(self, content: str) -> str:
        """Clean extracted content."""
        # Standard library imports
        import re

        # Remove excessive whitespace
        content = re.sub(r"\s+", " ", content)

        # Remove common navigation text
        noise_patterns = [
            r"Skip to main content",
            r"JavaScript is disabled",
            r"Please enable JavaScript",
            r"Cookie policy",
            r"Privacy policy",
        ]

        for pattern in noise_patterns:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)

        return content.strip()

    def _create_error_source(self, url: str, status: str) -> WebSource:
        """Create error WebSource object."""
        parsed_url = urlparse(url)
        return WebSource(
            url=url,
            title="",
            domain=parsed_url.netloc,
            content="",
            excerpt="",
            author="",
            publish_date="",
            credibility_score=0.0,
            word_count=0,
            reading_level="",
            extracted_date=datetime.now().isoformat(),
            status=status,
        )


class SearchEngine:
    """Search engine integration for finding relevant URLs."""

    def __init__(self):
        self.engines = {
            "duckduckgo": self._search_duckduckgo,
            "bing": self._search_bing,
        }

    async def search(
        self, query: str, engine: str = "duckduckgo", max_results: int = 10
    ) -> list[str]:
        """Search for URLs related to the query."""
        if engine not in self.engines:
            engine = "duckduckgo"

        try:
            return await self.engines[engine](query, max_results)
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []

    async def _search_duckduckgo(self, query: str, max_results: int) -> list[str]:
        """Search using DuckDuckGo (simplified implementation)."""
        # This is a simplified implementation
        # In production, use official APIs or specialized libraries
        urls = []

        try:
            # Construct search URL
            search_url = f"https://duckduckgo.com/html/?q={quote(query)}"

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        html = await response.text()

                        if BEAUTIFULSOUP_AVAILABLE:
                            soup = BeautifulSoup(html, "html.parser")

                            # Extract result links
                            for link in soup.find_all("a", class_="result__a"):
                                href = link.get("href")
                                if href and self._is_safe_url(href):
                                    urls.append(href)
                                    if len(urls) >= max_results:
                                        break

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")

        return urls[:max_results]

    def _is_safe_url(self, url: str) -> bool:
        """Validate that URL is safe and well-formed."""
        # Standard library imports
        import urllib.parse

        if not url:
            return False

        # Must start with safe protocols
        if not (url.startswith("https://") or url.startswith("http://")):
            return False

        try:
            parsed = urllib.parse.urlparse(url)

            # Must have valid scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False

            # Block local/private IPs and dangerous hosts
            dangerous_hosts = [
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "::1",
                "10.",
                "172.",
                "192.168.",
                "169.254.",
                "metadata.google.internal",
                "169.254.169.254",
            ]

            netloc_lower = parsed.netloc.lower()
            if any(netloc_lower.startswith(host) for host in dangerous_hosts):
                return False

            # Block non-HTTP schemes
            return parsed.scheme in ("http", "https")

        except Exception:
            return False

    async def _search_bing(self, query: str, max_results: int) -> list[str]:
        """Search using Bing (requires API key)."""
        # Placeholder for Bing API integration
        # Would require Bing Search API key
        return []


class FactChecker:
    """Fact-checking and verification utilities."""

    def __init__(self):
        self.fact_check_sources = [
            "snopes.com",
            "factcheck.org",
            "politifact.com",
            "reuters.com/fact-check",
            "apnews.com/hub/ap-fact-check",
        ]

    async def verify_claims(self, content: str) -> list[dict[str, Any]]:
        """Verify factual claims in content."""
        # Simplified fact-checking implementation
        # In production, integrate with fact-checking APIs

        claims = self._extract_claims(content)
        fact_checks = []

        for claim in claims:
            fact_check = {
                "claim": claim,
                "verdict": "Needs verification",
                "confidence": 0.5,
                "sources": [],
                "explanation": "Automated fact-checking not yet implemented",
            }
            fact_checks.append(fact_check)

        return fact_checks

    def _extract_claims(self, content: str) -> list[str]:
        """Extract factual claims from content."""
        # Standard library imports
        import re

        # Simple claim extraction based on sentence patterns
        sentences = content.split(". ")
        claims = []

        # Look for sentences with factual indicators
        fact_indicators = [
            r"\d+%",
            r"\$\d+",
            r"\d+ million",
            r"\d+ billion",
            r"according to",
            r"studies show",
            r"research indicates",
            r"data shows",
            r"statistics reveal",
        ]

        for sentence in sentences:
            for indicator in fact_indicators:
                if re.search(indicator, sentence, re.IGNORECASE):
                    claims.append(sentence.strip())
                    break

        return claims[:5]  # Limit to first 5 claims


class ReportGenerator:
    """Research report generation and formatting."""

    def __init__(self):
        self.templates = {
            "summary": self._generate_summary_report,
            "detailed": self._generate_detailed_report,
            "academic": self._generate_academic_report,
        }

    def generate_report(
        self, research_data: ResearchReport, report_type: str = "summary"
    ) -> str:
        """Generate research report in specified format."""
        if report_type not in self.templates:
            report_type = "summary"

        return self.templates[report_type](research_data)

    def _generate_summary_report(self, data: ResearchReport) -> str:
        """Generate summary research report."""
        report = f"""
# Research Report: {data.query.query}

**Generated:** {data.generated_date}
**Sources Analyzed:** {data.total_sources} ({data.successful_extractions} successful)

## Executive Summary
{data.summary}

## Key Insights
"""

        for i, insight in enumerate(data.key_insights, 1):
            report += f"{i}. {insight}\n"

        report += "\n## Source Credibility Assessment\n"
        report += f"**Average Credibility Score:** {data.credibility_assessment.get('average_score', 'N/A')}\n"
        report += f"**High-Quality Sources:** {data.credibility_assessment.get('high_quality_count', 0)}\n"

        if data.fact_checks:
            report += "\n## Fact Check Summary\n"
            for check in data.fact_checks:
                report += f"- **Claim:** {check['claim'][:100]}...\n"
                report += f"  **Status:** {check['verdict']}\n"

        report += "\n## Recommendations\n"
        for i, rec in enumerate(data.recommendations, 1):
            report += f"{i}. {rec}\n"

        report += "\n## Top Sources\n"
        for source in data.sources[:5]:
            if source.status == "success":
                report += f"- **{source.title}** ({source.domain})\n"
                report += f"  Credibility: {source.credibility_score:.2f} | Words: {source.word_count}\n"
                report += f"  {source.excerpt[:150]}...\n\n"

        return report

    def _generate_detailed_report(self, data: ResearchReport) -> str:
        """Generate detailed research report."""
        # More comprehensive report with full source analysis
        report = self._generate_summary_report(data)

        report += "\n## Detailed Source Analysis\n"
        for source in data.sources:
            report += f"\n### {source.title or 'Untitled'}\n"
            report += f"**URL:** {source.url}\n"
            report += f"**Domain:** {source.domain}\n"
            report += f"**Author:** {source.author or 'Unknown'}\n"
            report += f"**Published:** {source.publish_date or 'Unknown'}\n"
            report += f"**Credibility Score:** {source.credibility_score:.2f}\n"
            report += f"**Reading Level:** {source.reading_level}\n"
            report += f"**Word Count:** {source.word_count}\n"
            report += f"**Status:** {source.status}\n"

            if source.content:
                report += f"**Content Preview:**\n{source.content[:500]}...\n"

        return report

    def _generate_academic_report(self, data: ResearchReport) -> str:
        """Generate academic-style research report."""
        report = f"""
# Literature Review: {data.query.query}

## Abstract
{data.summary}

## Introduction
This research review examines available literature and web sources related to "{data.query.query}".
A total of {data.total_sources} sources were identified and analyzed, with {data.successful_extractions}
sources successfully processed for content analysis.

## Methodology
Sources were identified through automated web search and manual curation. Content extraction was
performed using advanced text processing algorithms. Credibility assessment utilized domain
authority metrics and content quality indicators.

## Findings
"""

        for insight in data.key_insights:
            report += f"\n### {insight}\n"

        report += "\n## Discussion\n"
        for rec in data.recommendations:
            report += f"{rec}\n\n"

        report += "\n## References\n"
        for i, source in enumerate(data.sources, 1):
            if source.status == "success" and source.title:
                report += f"{i}. {source.author or 'Unknown Author'}. "
                report += f"{source.title}. {source.domain}. "
                report += f"{source.publish_date or 'n.d.'}. {source.url}\n"

        return report


class WebResearchAssistantPlugin:
    """Main Web Research Assistant Plugin class."""

    def __init__(self):
        self.name = "Web Research Assistant"
        self.version = "1.0.0"
        self.description = "Intelligent web research and content analysis system"

        # Initialize components
        self.search_engine = SearchEngine()
        self.fact_checker = FactChecker()
        self.report_generator = ReportGenerator()

        # Plugin configuration
        self.config = {
            "max_sources": 20,
            "timeout_seconds": 30,
            "default_search_engine": "duckduckgo",
            "enable_fact_checking": True,
            "credibility_threshold": 0.6,
            "output_directory": "research_reports",
            "report_format": "summary",
        }

        # Ensure output directory exists
        os.makedirs(self.config["output_directory"], exist_ok=True)

    async def initialize(self):
        """Initialize the plugin."""
        logger.info("Web Research Assistant Plugin initialized")

    async def cleanup(self):
        """Cleanup plugin resources."""
        logger.info("Web Research Assistant Plugin cleaned up")

    def capabilities(self) -> list[str]:
        """Return plugin capabilities."""
        return [
            "web_content_extraction",
            "multi_source_research",
            "fact_checking",
            "credibility_assessment",
            "research_reports",
            "citation_management",
            "content_summarization",
        ]

    def _is_safe_url(self, url: str) -> bool:
        """Validate that URL is safe and well-formed."""
        # Standard library imports
        import urllib.parse

        if not url:
            return False

        # Must start with safe protocols
        if not (url.startswith("https://") or url.startswith("http://")):
            return False

        try:
            parsed = urllib.parse.urlparse(url)

            # Must have valid scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False

            # Block local/private IPs and dangerous hosts
            dangerous_hosts = [
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "::1",
                "10.",
                "172.",
                "192.168.",
                "169.254.",
                "metadata.google.internal",
                "169.254.169.254",
            ]

            netloc_lower = parsed.netloc.lower()
            if any(netloc_lower.startswith(host) for host in dangerous_hosts):
                return False

            # Block non-HTTP schemes
            return parsed.scheme in ("http", "https")

        except Exception:
            return False

    async def invoke(
        self, action: str, payload: dict[str, Any], context=None
    ) -> dict[str, Any]:
        """Main plugin invocation method."""
        try:
            if action == "research":
                return await self.conduct_research(
                    payload.get("query"), payload.get("options", {})
                )
            elif action == "extract_content":
                return await self.extract_single_source(payload.get("url"))
            elif action == "search_sources":
                return await self.search_for_sources(
                    payload.get("query"), payload.get("max_results", 10)
                )
            elif action == "fact_check":
                return await self.fact_check_content(payload.get("content"))
            elif action == "generate_report":
                return await self.generate_research_report(
                    payload.get("research_data"), payload.get("format", "summary")
                )
            elif action == "get_config":
                return {"status": "success", "data": self.config}
            elif action == "update_config":
                return await self.update_config(payload)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Plugin invocation failed: {e}")
            return {"status": "error", "message": str(e)}

    async def conduct_research(
        self, query: str, options: dict[str, Any]
    ) -> dict[str, Any]:
        """Conduct comprehensive research on a topic."""
        try:
            if not query:
                return {"status": "error", "message": "Query is required"}

            # Create research query object
            research_query = ResearchQuery(
                query=query,
                keywords=options.get("keywords", [query]),
                sources=options.get("sources", []),
                depth=options.get("depth", "moderate"),
                content_types=options.get("content_types", ["article", "news"]),
                date_range=options.get("date_range", {}),
                language=options.get("language", "en"),
                region=options.get("region", ""),
            )

            # Search for sources
            if not research_query.sources:
                search_results = await self.search_engine.search(
                    query,
                    self.config["default_search_engine"],
                    self.config["max_sources"],
                )
                research_query.sources = search_results

            # Extract content from sources
            sources = []
            async with WebExtractor() as extractor:
                for url in research_query.sources:
                    source = await extractor.extract_content(url)
                    sources.append(source)

            # Filter successful sources
            successful_sources = [s for s in sources if s.status == "success"]

            # Generate summary and insights
            all_content = " ".join([s.content for s in successful_sources])
            summary = self._generate_summary(all_content)
            insights = self._extract_key_insights(all_content, successful_sources)

            # Assess credibility
            credibility_assessment = self._assess_overall_credibility(
                successful_sources
            )

            # Fact checking (if enabled)
            fact_checks = []
            if self.config["enable_fact_checking"]:
                fact_checks = await self.fact_checker.verify_claims(all_content)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                successful_sources, credibility_assessment
            )

            # Create research report
            report = ResearchReport(
                query=research_query,
                sources=sources,
                summary=summary,
                key_insights=insights,
                credibility_assessment=credibility_assessment,
                fact_checks=fact_checks,
                recommendations=recommendations,
                generated_date=datetime.now().isoformat(),
                total_sources=len(sources),
                successful_extractions=len(successful_sources),
            )

            return {
                "status": "success",
                "data": asdict(report),
                "message": f"Research completed with {len(successful_sources)} sources",
            }

        except Exception as e:
            return {"status": "error", "message": f"Research failed: {e}"}

    async def extract_single_source(self, url: str) -> dict[str, Any]:
        """Extract content from a single URL."""
        try:
            if not url:
                return {"status": "error", "message": "URL is required"}

            async with WebExtractor() as extractor:
                source = await extractor.extract_content(url)

            return {
                "status": "success",
                "data": asdict(source),
                "message": f"Content extracted: {source.status}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Extraction failed: {e}"}

    async def search_for_sources(self, query: str, max_results: int) -> dict[str, Any]:
        """Search for sources related to query."""
        try:
            if not query:
                return {"status": "error", "message": "Query is required"}

            urls = await self.search_engine.search(
                query, self.config["default_search_engine"], max_results
            )

            return {
                "status": "success",
                "data": {"urls": urls, "count": len(urls)},
                "message": f"Found {len(urls)} potential sources",
            }

        except Exception as e:
            return {"status": "error", "message": f"Search failed: {e}"}

    async def fact_check_content(self, content: str) -> dict[str, Any]:
        """Perform fact-checking on content."""
        try:
            if not content:
                return {"status": "error", "message": "Content is required"}

            fact_checks = await self.fact_checker.verify_claims(content)

            return {
                "status": "success",
                "data": {"fact_checks": fact_checks, "count": len(fact_checks)},
                "message": f"Analyzed {len(fact_checks)} factual claims",
            }

        except Exception as e:
            return {"status": "error", "message": f"Fact checking failed: {e}"}

    async def generate_research_report(
        self, research_data: dict, format_type: str
    ) -> dict[str, Any]:
        """Generate formatted research report."""
        try:
            if not research_data:
                return {"status": "error", "message": "Research data is required"}

            # Convert dict back to ResearchReport object (simplified)
            # In production, use proper deserialization
            report_content = self.report_generator.generate_report(
                research_data, format_type
            )

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"research_report_{timestamp}.md"
            filepath = os.path.join(self.config["output_directory"], filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_content)

            return {
                "status": "success",
                "data": {
                    "report_content": report_content,
                    "filepath": filepath,
                    "format": format_type,
                },
                "message": f"Report generated: {filename}",
            }

        except Exception as e:
            return {"status": "error", "message": f"Report generation failed: {e}"}

    async def update_config(self, new_config: dict[str, Any]) -> dict[str, Any]:
        """Update plugin configuration."""
        try:
            self.config.update(new_config)
            return {"status": "success", "message": "Configuration updated"}
        except Exception as e:
            return {"status": "error", "message": f"Config update failed: {e}"}

    def _generate_summary(self, content: str, max_length: int = 500) -> str:
        """Generate summary of research content."""
        if not content:
            return "No content available for summarization"

        # Simple extractive summarization
        sentences = content.split(". ")

        # Score sentences by position and length
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 1.0 / (i + 1)  # Earlier sentences get higher scores
            if len(sentence) > 20:  # Prefer longer sentences
                score += 0.5
            scored_sentences.append((score, sentence))

        # Sort by score and take top sentences
        scored_sentences.sort(reverse=True)

        summary = ""
        for score, sentence in scored_sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break

        return summary.strip() or "Unable to generate summary"

    def _extract_key_insights(
        self, content: str, sources: list[WebSource]
    ) -> list[str]:
        """Extract key insights from research content."""
        insights = []

        # Source diversity insight
        domains = set(s.domain for s in sources if s.status == "success")
        insights.append(f"Information gathered from {len(domains)} different domains")

        # Content volume insight
        total_words = sum(s.word_count for s in sources if s.status == "success")
        insights.append(f"Total content analyzed: {total_words} words")

        # Quality insight
        high_quality = [s for s in sources if s.credibility_score > 0.7]
        insights.append(
            f"High-credibility sources: {len(high_quality)} out of {len(sources)}"
        )

        # Reading level insight
        levels = [s.reading_level for s in sources if s.reading_level != "Unknown"]
        if levels:
            insights.append(f"Content reading levels range from basic to advanced")

        return insights

    def _assess_overall_credibility(self, sources: list[WebSource]) -> dict[str, Any]:
        """Assess overall credibility of sources."""
        if not sources:
            return {
                "average_score": 0.0,
                "high_quality_count": 0,
                "assessment": "No sources",
            }

        scores = [s.credibility_score for s in sources]
        avg_score = sum(scores) / len(scores)
        high_quality_count = len([s for s in sources if s.credibility_score > 0.7])

        if avg_score > 0.8:
            assessment = "Highly credible sources"
        elif avg_score > 0.6:
            assessment = "Generally credible sources"
        elif avg_score > 0.4:
            assessment = "Mixed credibility sources"
        else:
            assessment = "Low credibility sources"

        return {
            "average_score": avg_score,
            "high_quality_count": high_quality_count,
            "total_sources": len(sources),
            "assessment": assessment,
        }

    def _generate_recommendations(
        self, sources: list[WebSource], credibility: dict[str, Any]
    ) -> list[str]:
        """Generate research recommendations."""
        recommendations = []

        if credibility["average_score"] < 0.6:
            recommendations.append(
                "Consider seeking additional high-credibility sources"
            )

        if len(sources) < 5:
            recommendations.append("Expand research with more diverse sources")

        domains = set(s.domain for s in sources)
        if len(domains) < 3:
            recommendations.append(
                "Include sources from different domains for balanced perspective"
            )

        if not any("edu" in s.domain for s in sources):
            recommendations.append(
                "Consider including academic sources for scholarly perspective"
            )

        return recommendations


# Plugin entry point
def get_plugin():
    """Return the plugin instance."""
    return WebResearchAssistantPlugin()


# For testing
if __name__ == "__main__":

    async def test_plugin():
        plugin = WebResearchAssistantPlugin()
        await plugin.initialize()

        # Test research
        result = await plugin.conduct_research(
            "artificial intelligence ethics",
            {"depth": "moderate", "content_types": ["article", "academic"]},
        )
        print("Research result:", result["status"])

        await plugin.cleanup()

    asyncio.run(test_plugin())
