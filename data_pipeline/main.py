import logging
import time
import os
import pandas as pd

from scraper import scrape_books
from cleaning import clean_data
from database import create_connection, setup_database, insert_data
from queries import execute_and_export_queries, verify_pandas_merge

def setup_logging():
    """Configure logging for the pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s %(message)s'
    )

def main():
    start_time = time.time()
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ETL Pipeline...")
    
    # 1. Extract (Scraping)
    raw_books = scrape_books(pages=5)
    total_scraped = len(raw_books)
    
    # 2. Transform (Cleaning & Currency Conversion)
    cleaned_books = clean_data(raw_books)
    total_retained = len(cleaned_books)
    total_dropped = total_scraped - total_retained
    
    # Save cleaned data to CSV
    os.makedirs("data", exist_ok=True)
    cleaned_csv_path = "data/books_cleaned.csv"
    df_cleaned = pd.DataFrame(cleaned_books)
    df_cleaned.to_csv(cleaned_csv_path, index=False)
    logger.info(f"Cleaned data saved to {cleaned_csv_path}")
    
    # 3. Load (SQLite Database)
    conn = create_connection()
    try:
        setup_database(conn)
        insert_data(conn, cleaned_books)
        
        # 4. Analysis (SQL Queries)
        execute_and_export_queries(conn)
        
        # 5. Pandas Merge Verification
        join_verified = verify_pandas_merge(conn)
        
        # Calculate categories
        categories_count = pd.read_sql("SELECT COUNT(*) FROM categories", conn).iloc[0, 0]
        
    finally:
        conn.close()
        logger.info("Database connection closed.")
        
    execution_time = time.time() - start_time
    
    # End-of-Pipeline Summary
    summary = f"""
====================================
ETL PIPELINE COMPLETED SUCCESSFULLY
====================================

Books scraped      : {total_scraped}
Books retained     : {total_retained}
Rows dropped       : {total_dropped}
Categories         : {categories_count}
Database           : books.db
SQL queries run    : 6
CSV exports        : 6
Join verified      : {'PASS' if join_verified else 'FAIL'}
Execution time     : {execution_time:.2f} seconds
"""
    print(summary)

if __name__ == "__main__":
    main()
