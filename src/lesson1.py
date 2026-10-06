import urllib.request
import json
from db_connection import save_bitcoin_price
from logger_config import logger
# ----------------------------------------------------
# 1. EXTRACT: Lấy giá Bitcoin từ Internet
# ----------------------------------------------------
url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode())
    btc_price = data["bitcoin"]["usd"]
    logger.info(f"1. Lay gia Bitcoin thanh cong: {btc_price:,} USD")
except Exception as e:
    logger.error(f"Loi khi lay gia Bitcoin: {e}")
    exit()

# ----------------------------------------------------
# 2. LOAD: Bắn dữ liệu vào MS SQL Server
# ----------------------------------------------------
save_bitcoin_price(btc_price)

from db_connection import save_crypto_batch

url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    response = urllib.request.urlopen(req)
    raw_data = json.loads(response.read().decode())
    
    # 2. TRANSFORM: Flatten the nested JSON structure into a list of tuples
    records_to_insert = []
    
    for symbol, details in raw_data.items():
        price = details.get("usd", 0)
        market_cap = details.get("usd_market_cap", 0)
        volume_24h = details.get("usd_24h_vol", 0)
        
        # Append tuple matching the SQL column order
        records_to_insert.append((symbol, price, market_cap, volume_24h))
        
        print(f"Extracted {symbol.upper()}: Price=\({price:,.2f} | MarketCap=\){market_cap:,.0f}")

    # 3. LOAD: Pass the cleaned list to the database module
    if records_to_insert:
        save_crypto_batch(records_to_insert)

except Exception as e:
    logger.error(f"Pipeline error: {e}")