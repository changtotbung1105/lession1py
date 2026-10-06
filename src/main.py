import urllib.request
import urllib.error
import json
import time
from src.db_connection import save_crypto_batch
from src.logger_config import logger


API_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin,ethereum,solana"
    "&vs_currencies=usd"
    "&include_market_cap=true"
    "&include_24hr_vol=true"
)
# API_URL = "https://invalid-domain-coingecko-test.com/api"
# Pipeline resilience configuration


MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 10

def validate_crypto_record(symbol, price, market_cap, volume):
    """
    Validates record structure and numerical values.
    Returns True if valid, False otherwise.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        logger.warning(f"Validation failed: Invalid symbol '{symbol}'")
        return False

    if not isinstance(price, (int, float)) or price <= 0:
        logger.warning(f"Validation failed: Invalid price ({price}) for symbol '{symbol}'")
        return False

    if not isinstance(market_cap, (int, float)) or market_cap < 0:
        logger.warning(f"Validation failed: Invalid market cap ({market_cap}) for symbol '{symbol}'")
        return False

    return True

def fetch_crypto_data_with_retry(url):
    """
    Fetches JSON data from API with explicit timeouts and exponential backoff.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    backoff = INITIAL_BACKOFF_SECONDS

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetch attempt {attempt} of {MAX_RETRIES}...")
            backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))  # Exponential backoff
            # Request with explicit timeout setting
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                if response.status == 200:
                    raw_data = json.loads(response.read().decode())
                    logger.info("API payload successfully retrieved.")
                    return raw_data

        except urllib.error.HTTPError as e:
            # Handle API Rate Limits (429) or Server Errors (500, 502, 503)
            logger.info(f"HTTP Error {e.code}: {e.reason}")
            
            if e.code == 429:
                logger.info("Rate limit exceeded (HTTP 429). Retrying with backoff...")
            elif e.code >= 500:
                logger.info("Server error on target API. Retrying...")
            else:
                # Client-side errors like 400 or 404 shouldn't be retried
                logger.info("Unrecoverable client error. Aborting fetch.")
                raise e

        except urllib.error.URLError as e:
            # Handle Network Timeouts or DNS resolution failures
            logger.info(f"Network error / Connection failure: {e.reason}")

        except Exception as e:
            logger.info(f"Unexpected error during fetch: {e}")

        # Execute exponential backoff before next attempt
        if attempt < MAX_RETRIES:
            logger.info(f"Waiting {backoff} seconds before retrying...")
            time.sleep(backoff)
            backoff *= 2  # Exponential increase (2s -> 4s -> 8s)
        else:
            logger.info("Maximum retry limit reached. Pipeline fetch failed.")

    return None


# ----------------------------------------------------
# Main Execution Flow
# ----------------------------------------------------
def run_pipeline():
    # 1. EXTRACT (With Retry Logic)
    raw_data = fetch_crypto_data_with_retry(API_URL)
    
    if not raw_data:
        logger.info("Pipeline stopped: No data fetched.")
        return

    # 2. TRANSFORM
    records_to_insert = []
    for symbol, details in raw_data.items():
        price = details.get("usd", 0)
        market_cap = details.get("usd_market_cap", 0)
        volume_24h = details.get("usd_24h_vol", 0)
        records_to_insert.append((symbol, price, market_cap, volume_24h))

    # 3. LOAD
    if records_to_insert:
        save_crypto_batch(records_to_insert)


if __name__ == "__main__":
    run_pipeline()