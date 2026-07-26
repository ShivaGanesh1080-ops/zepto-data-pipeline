import logging
from typing import List, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

BASE_URL = "http://books.toscrape.com/catalogue/"

def create_session() -> requests.Session:
    """Create and configure a requests session with retries."""
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def extract_category_from_detail(session: requests.Session, detail_url: str) -> str:
    """Fetch the book detail page and extract the category from the breadcrumb."""
    try:
        response = session.get(detail_url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        
        # Breadcrumb structure: Home > Books > [Category] > [Title]
        breadcrumb = soup.find("ul", class_="breadcrumb")
        if breadcrumb:
            links = breadcrumb.find_all("a")
            if len(links) >= 3:
                return links[2].text.strip()
    except Exception as e:
        logger.warning(f"Failed to extract category from {detail_url}: {e}")
    
    return "Unknown"

def scrape_books(pages: int = 5) -> List[Dict[str, Any]]:
    """Scrape the first `pages` of the 'All Products' catalogue."""
    session = create_session()
    books = []
    
    logger.info(f"Starting scraper for {pages} pages...")
    
    for page in range(1, pages + 1):
        url = f"{BASE_URL}page-{page}.html"
        try:
            logger.info(f"Scraping page {page}: {url}")
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            articles = soup.find_all("article", class_="product_pod")
            
            for article in articles:
                # Title
                h3 = article.find("h3")
                a_tag = h3.find("a") if h3 else None
                title = a_tag["title"] if a_tag and "title" in a_tag.attrs else "Unknown Title"
                
                # Price
                price_tag = article.find("p", class_="price_color")
                price = price_tag.text.strip() if price_tag else ""
                
                # Rating
                rating_tag = article.find("p", class_="star-rating")
                rating = "Unknown"
                if rating_tag and len(rating_tag.get("class", [])) > 1:
                    rating = rating_tag["class"][1]
                    
                # Availability
                avail_tag = article.find("p", class_="instock availability")
                availability = avail_tag.text.strip() if avail_tag else ""
                
                # Detail URL and Category
                detail_href = a_tag["href"] if a_tag else ""
                category = "Unknown"
                if detail_href:
                    detail_url = urljoin(url, detail_href)
                    category = extract_category_from_detail(session, detail_url)
                
                books.append({
                    "title": title,
                    "price": price,
                    "star_rating": rating,
                    "availability": availability,
                    "category": category
                })
                
        except Exception as e:
            logger.error(f"Failed to scrape page {page}: {e}")
            
    logger.info(f"Scraping completed. Extracted {len(books)} books.")
    return books
