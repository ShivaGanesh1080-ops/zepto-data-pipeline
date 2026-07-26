import sqlite3
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

DB_PATH = "books.db"

def create_connection(db_file: str = DB_PATH) -> sqlite3.Connection:
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(db_file)
    # Explicitly enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def setup_database(conn: sqlite3.Connection):
    """Create the normalized tables with constraints."""
    cursor = conn.cursor()
    
    # Drop existing tables to ensure idempotency when running main.py multiple times
    cursor.execute("DROP TABLE IF EXISTS books;")
    cursor.execute("DROP TABLE IF EXISTS categories;")
    
    # Create categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL
        )
    """)
    
    # Create books table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY(category_id) REFERENCES categories(category_id)
        )
    """)
    
    conn.commit()
    logger.info("Database schema created successfully.")

def insert_data(conn: sqlite3.Connection, cleaned_books: List[Dict[str, Any]]):
    """Insert cleaned data into the database."""
    cursor = conn.cursor()
    
    category_map = {}
    
    for book in cleaned_books:
        cat_name = book["category_name"]
        
        # Insert category if not exists
        if cat_name not in category_map:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (category_name)
                VALUES (?)
            """, (cat_name,))
            
            # Fetch the category_id
            cursor.execute("SELECT category_id FROM categories WHERE category_name = ?", (cat_name,))
            row = cursor.fetchone()
            if row:
                category_map[cat_name] = row[0]
                
        category_id = category_map[cat_name]
        
        # Insert book
        cursor.execute("""
            INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            book["title"],
            book["price_gbp"],
            book["price_inr"],
            book["rating"],
            int(book["in_stock"]), # SQLite doesn't have a boolean type, integer 1/0 is used
            category_id
        ))
        
    conn.commit()
    logger.info(f"Inserted {len(cleaned_books)} records into the database.")
