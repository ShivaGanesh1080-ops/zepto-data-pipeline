import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

GBP_TO_INR_RATE = 105.50

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def clean_data(raw_books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean the scraped data and convert currencies. Drops malformed rows."""
    cleaned_books = []
    dropped_count = 0
    
    logger.info("Starting data cleaning process...")
    
    for book in raw_books:
        title = book.get("title", "")
        
        try:
            # Clean price
            raw_price = book.get("price", "")
            import re
            match = re.search(r'[\d\.]+', raw_price)
            if not match:
                raise ValueError(f"Invalid price format: {raw_price}")
            
            price_gbp = float(match.group())
            
            # Currency conversion
            price_inr = round(price_gbp * GBP_TO_INR_RATE, 2)
            
            # Clean rating
            raw_rating = book.get("star_rating", "")
            if raw_rating not in RATING_MAP:
                raise ValueError(f"Invalid rating: {raw_rating}")
            rating = RATING_MAP[raw_rating]
            
            # Clean availability
            raw_avail = book.get("availability", "").lower()
            if "in stock" in raw_avail:
                in_stock = True
            elif "out of stock" in raw_avail:
                in_stock = False
            else:
                raise ValueError(f"Invalid availability: {raw_avail}")
            
            # Clean category
            category = book.get("category", "")
            if not category or category == "Unknown":
                raise ValueError("Missing or unknown category")
                
            cleaned_books.append({
                "title": title,
                "price_gbp": price_gbp,
                "price_inr": price_inr,
                "rating": rating,
                "in_stock": in_stock,
                "category_name": category
            })
            
        except ValueError as e:
            logger.warning(f"Row dropped. Title: {title}. Reason: {e}")
            dropped_count += 1
            
    logger.info(f"Data cleaning completed. Retained: {len(cleaned_books)}, Dropped: {dropped_count}")
    return cleaned_books
