import os
import pyodbc
from dotenv import load_dotenv

# Load key-value pairs from .env into system environment variables
load_dotenv()

# Read variables dynamically from the environment
SERVER_NAME = os.getenv("DB_SERVER", "localhost")
DATABASE_NAME = os.getenv("DB_NAME", "YourDatabaseName")
DB_DRIVER = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")


def get_connection():
    """Establishes a SQL Server connection using environment configuration."""
    conn_str = (
        f"DRIVER={DB_DRIVER};"
        f"SERVER={SERVER_NAME};"
        f"DATABASE={DATABASE_NAME};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    return pyodbc.connect(conn_str)

def save_bitcoin_price(price):
    """Inserts the Bitcoin price into MS SQL Server."""
    conn = get_connection()
    cursor = conn.cursor()
    insert_sql = "INSERT INTO BitcoinHistory (Price) VALUES (?)"
    cursor.execute(insert_sql, (price,))
    conn.commit()
    print("Successfully inserted record into SQL Server!")
    cursor.close()
    conn.close()

def save_crypto_batch(crypto_list):
    """Function 2: Inserts multiple rows into MS SQL Server."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        insert_sql = """
            INSERT INTO CryptoPrices (Symbol, PriceUSD, MarketCapUSD, Volume24hUSD)
            VALUES (?, ?, ?, ?)
        """
        
        cursor.executemany(insert_sql, crypto_list)
        conn.commit()
        
        print(f"Successfully inserted {len(crypto_list)} records!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print("Database error:", e)
        