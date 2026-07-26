import sqlite3
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

def execute_and_export_queries(conn: sqlite3.Connection):
    """Execute SQL queries, save to CSV, and print results using pandas."""
    os.makedirs("outputs", exist_ok=True)
    
    queries = {
        "query1_select_where": """
            -- 1. Books with rating >= 4 (SELECT + WHERE)
            SELECT title, rating 
            FROM books 
            WHERE rating >= 4;
        """,
        "query2_order_limit": """
            -- 2. Most expensive books (ORDER BY + LIMIT)
            SELECT title, price_gbp 
            FROM books 
            ORDER BY price_gbp DESC 
            LIMIT 5;
        """,
        "query3_distinct": """
            -- 3. DISTINCT categories
            SELECT DISTINCT category_name 
            FROM categories;
        """,
        "query4_between": """
            -- 4. Books priced BETWEEN two values
            SELECT title, price_gbp 
            FROM books 
            WHERE price_gbp BETWEEN 10.00 AND 20.00;
        """,
        "query5_in": """
            -- 5. Books with ratings IN (4,5)
            SELECT title, rating 
            FROM books 
            WHERE rating IN (4, 5);
        """,
        "query6_join": """
            -- 6. JOIN books with categories
            SELECT b.title, b.price_gbp, c.category_name 
            FROM books b
            JOIN categories c ON b.category_id = c.category_id;
        """
    }
    
    logger.info("Executing SQL queries...")
    for idx, (name, sql) in enumerate(queries.items(), 1):
        df = pd.read_sql(sql, conn)
        
        # Save to CSV
        csv_path = f"outputs/query{idx}.csv"
        df.to_csv(csv_path, index=False)
        
        # Print results
        print(f"\n--- Query {idx}: {name} ---")
        print(df.head())
        logger.info(f"Query {idx} executed and exported to {csv_path}")

def verify_pandas_merge(conn: sqlite3.Connection):
    """Reproduce the SQL JOIN using pd.merge and verify equivalence."""
    logger.info("Verifying SQL JOIN against Pandas merge...")
    
    # Run the SQL JOIN
    sql_join_query = """
        SELECT b.title, b.price_gbp, c.category_name 
        FROM books b
        JOIN categories c ON b.category_id = c.category_id;
    """
    sql_df = pd.read_sql(sql_join_query, conn)
    
    # Read tables into pandas
    books_df = pd.read_sql("SELECT * FROM books;", conn)
    categories_df = pd.read_sql("SELECT * FROM categories;", conn)
    
    # Perform the pandas merge
    merge_df = pd.merge(books_df, categories_df, on="category_id", how="inner")
    # Select and order the columns to match the SQL query exactly
    merge_df = merge_df[["title", "price_gbp", "category_name"]]
    
    print("\n--- SQL JOIN DataFrame ---")
    print(sql_df.head())
    
    print("\n--- Pandas Merge DataFrame ---")
    print(merge_df.head())
    
    are_equal = sql_df.equals(merge_df)
    print(f"\nJoin verified equivalent: {are_equal}")
    logger.info(f"Pandas merge equivalence check: {are_equal}")
    
    return are_equal
