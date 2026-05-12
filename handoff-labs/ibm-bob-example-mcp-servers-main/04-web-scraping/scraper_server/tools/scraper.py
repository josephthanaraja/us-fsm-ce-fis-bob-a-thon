"""
Web scraping and content extraction tools.

This module provides tools for fetching web content, parsing HTML,
extracting structured data, and handling different content types.
"""

import logging
import json
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScraper:
    """Manages web scraping operations."""
    
    def __init__(self, timeout: int = 30, user_agent: Optional[str] = None):
        self.timeout = timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
    
    def fetch_url(self, url: str, headers: Optional[Dict] = None) -> requests.Response:
        """Fetch content from a URL."""
        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
                headers=headers or {},
                allow_redirects=True,
                verify=False  # Disable SSL verification
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            raise
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'html.parser')


def create_scraper_tools(mcp, timeout: int, user_agent: str):
    """Register all web scraping tools with the MCP server."""
    
    scraper = WebScraper(timeout, user_agent)
    
    @mcp.tool()
    def fetch_webpage(url: str, custom_headers: str = "{}") -> str:
        """
        Fetch the full HTML content of a webpage.
        
        Args:
            url: The URL to fetch
            custom_headers: Optional JSON string with custom HTTP headers
        
        Returns:
            JSON string with status, URL, and content
        
        Example:
            fetch_webpage("https://example.com")
            fetch_webpage("https://api.example.com", '{"Authorization": "Bearer token"}')
        """
        try:
            headers = json.loads(custom_headers) if custom_headers != "{}" else {}
            response = scraper.fetch_url(url, headers)
            
            result = {
                "url": response.url,
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "content_length": len(response.content),
                "content": response.text[:50000]  # Limit to first 50KB
            }
            
            logger.info(f"Fetched {url} - Status: {response.status_code}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error fetching webpage: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def extract_links(url: str, filter_pattern: str = "") -> str:
        """
        Extract all links from a webpage.
        
        Args:
            url: The URL to scrape
            filter_pattern: Optional regex pattern to filter links
        
        Returns:
            JSON string with list of links
        
        Example:
            extract_links("https://example.com")
            extract_links("https://example.com", r".*\.pdf$")
        """
        try:
            response = scraper.fetch_url(url)
            soup = scraper.parse_html(response.text)
            
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = urljoin(url, href)
                
                # Apply filter if provided
                if filter_pattern and not re.search(filter_pattern, absolute_url):
                    continue
                
                links.append({
                    "url": absolute_url,
                    "text": a_tag.get_text(strip=True),
                    "title": a_tag.get('title', '')
                })
            
            result = {
                "source_url": url,
                "total_links": len(links),
                "links": links
            }
            
            logger.info(f"Extracted {len(links)} links from {url}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error extracting links: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def extract_text(url: str, selector: str = "") -> str:
        """
        Extract text content from a webpage.
        
        Args:
            url: The URL to scrape
            selector: Optional CSS selector to target specific elements
        
        Returns:
            JSON string with extracted text
        
        Example:
            extract_text("https://example.com")
            extract_text("https://example.com", "article p")
        """
        try:
            response = scraper.fetch_url(url)
            soup = scraper.parse_html(response.text)
            
            if selector:
                elements = soup.select(selector)
                text = "\n\n".join([elem.get_text(strip=True) for elem in elements])
            else:
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator="\n", strip=True)
            
            result = {
                "url": url,
                "selector": selector or "entire page",
                "text_length": len(text),
                "text": text[:10000]  # Limit to first 10KB
            }
            
            logger.info(f"Extracted text from {url}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error extracting text: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def extract_metadata(url: str) -> str:
        """
        Extract metadata from a webpage (title, description, Open Graph tags, etc.).
        
        Args:
            url: The URL to scrape
        
        Returns:
            JSON string with metadata
        
        Example:
            extract_metadata("https://example.com")
        """
        try:
            response = scraper.fetch_url(url)
            soup = scraper.parse_html(response.text)
            
            metadata = {
                "url": url,
                "title": "",
                "description": "",
                "keywords": "",
                "author": "",
                "og_tags": {},
                "twitter_tags": {}
            }
            
            # Extract title
            if soup.title:
                metadata["title"] = soup.title.string
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name', '').lower()
                property_name = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                if name == 'description':
                    metadata["description"] = content
                elif name == 'keywords':
                    metadata["keywords"] = content
                elif name == 'author':
                    metadata["author"] = content
                elif property_name.startswith('og:'):
                    metadata["og_tags"][property_name] = content
                elif name.startswith('twitter:'):
                    metadata["twitter_tags"][name] = content
            
            logger.info(f"Extracted metadata from {url}")
            return json.dumps(metadata, indent=2)
        except Exception as e:
            error_msg = f"Error extracting metadata: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def extract_images(url: str, min_width: int = 0, min_height: int = 0) -> str:
        """
        Extract all images from a webpage.
        
        Args:
            url: The URL to scrape
            min_width: Minimum image width (0 = no filter)
            min_height: Minimum image height (0 = no filter)
        
        Returns:
            JSON string with list of images
        
        Example:
            extract_images("https://example.com")
            extract_images("https://example.com", 300, 300)
        """
        try:
            response = scraper.fetch_url(url)
            soup = scraper.parse_html(response.text)
            
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if not src:
                    continue
                
                absolute_url = urljoin(url, src)
                width = img.get('width', 0)
                height = img.get('height', 0)
                
                # Try to convert width/height to int
                try:
                    width = int(width) if width else 0
                    height = int(height) if height else 0
                except (ValueError, TypeError):
                    width = height = 0
                
                # Apply size filters
                if min_width > 0 and width > 0 and width < min_width:
                    continue
                if min_height > 0 and height > 0 and height < min_height:
                    continue
                
                images.append({
                    "url": absolute_url,
                    "alt": img.get('alt', ''),
                    "title": img.get('title', ''),
                    "width": width,
                    "height": height
                })
            
            result = {
                "source_url": url,
                "total_images": len(images),
                "images": images
            }
            
            logger.info(f"Extracted {len(images)} images from {url}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error extracting images: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def extract_structured_data(url: str, selector: str, attributes: str) -> str:
        """
        Extract structured data from specific elements on a webpage.
        
        Args:
            url: The URL to scrape
            selector: CSS selector for target elements
            attributes: JSON array of attribute names to extract (e.g., '["text", "href", "class"]')
        
        Returns:
            JSON string with extracted structured data
        
        Example:
            extract_structured_data("https://example.com", "article.post", '["text", "data-id"]')
            extract_structured_data("https://news.com", "h2.headline a", '["text", "href"]')
        """
        try:
            response = scraper.fetch_url(url)
            soup = scraper.parse_html(response.text)
            attrs = json.loads(attributes)
            
            elements = soup.select(selector)
            data = []
            
            for elem in elements:
                item = {}
                for attr in attrs:
                    if attr == "text":
                        item["text"] = elem.get_text(strip=True)
                    elif attr == "html":
                        item["html"] = str(elem)
                    else:
                        item[attr] = elem.get(attr, "")
                data.append(item)
            
            result = {
                "url": url,
                "selector": selector,
                "total_elements": len(data),
                "data": data
            }
            
            logger.info(f"Extracted {len(data)} structured elements from {url}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error extracting structured data: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def extract_tables(url: str, table_index: int = -1) -> str:
        """
        Extract table data from a webpage.
        
        Args:
            url: The URL to scrape
            table_index: Index of specific table to extract (-1 = all tables)
        
        Returns:
            JSON string with table data
        
        Example:
            extract_tables("https://example.com")
            extract_tables("https://example.com", 0)
        """
        try:
            response = scraper.fetch_url(url)
            soup = scraper.parse_html(response.text)
            
            tables = soup.find_all('table')
            
            if table_index >= 0:
                if table_index >= len(tables):
                    return json.dumps({"error": f"Table index {table_index} out of range. Found {len(tables)} tables."})
                tables = [tables[table_index]]
            
            result = {
                "url": url,
                "total_tables": len(tables),
                "tables": []
            }
            
            for idx, table in enumerate(tables):
                table_data = {
                    "index": idx,
                    "headers": [],
                    "rows": []
                }
                
                # Extract headers
                headers = table.find_all('th')
                if headers:
                    table_data["headers"] = [th.get_text(strip=True) for th in headers]
                
                # Extract rows
                for tr in table.find_all('tr'):
                    cells = tr.find_all(['td', 'th'])
                    if cells:
                        row = [cell.get_text(strip=True) for cell in cells]
                        table_data["rows"].append(row)
                
                result["tables"].append(table_data)
            
            logger.info(f"Extracted {len(tables)} table(s) from {url}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error extracting tables: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    @mcp.tool()
    def search_openverse_images(query: str, page_size: int = 5) -> str:
        """
        Search for images using the Openverse API.
        
        Args:
            query: Search query (e.g., "airplane wing", "sunset beach")
            page_size: Number of results to return (default: 5, max: 20)
        
        Returns:
            JSON string with list of images and their metadata
        
        Example:
            search_openverse_images("airplane wing")
            search_openverse_images("sunset beach", 10)
        """
        try:
            # Limit page_size to reasonable bounds
            page_size = min(max(1, page_size), 20)
            
            response = requests.get(
                "https://api.openverse.org/v1/images/",
                params={"q": query, "page_size": page_size},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title"),
                    "image_url": item.get("url"),          # where the work lives
                    "thumbnail": item.get("thumbnail"),    # preview
                    "license": item.get("license"),
                    "license_version": item.get("license_version"),
                    "license_url": item.get("license_url"),
                    "creator": item.get("creator"),
                    "creator_url": item.get("creator_url"),
                    "attribution": item.get("attribution"),
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "source": item.get("source"),
                })
            
            result = {
                "query": query,
                "total_results": len(results),
                "page_size": page_size,
                "results": results
            }
            
            logger.info(f"Found {len(results)} images for query: {query}")
            return json.dumps(result, indent=2)
        except Exception as e:
            error_msg = f"Error searching Openverse images: {str(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg})
    
    logger.info("Web scraping tools registered successfully")

# Made with Bob