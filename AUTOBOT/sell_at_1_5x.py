"""
FINAL TESTNET VERSION - Binance Spot Testnet Bot
------------------------------------------------
✅ Monitors BTC price on Binance Testnet
✅ Sells when current price >= entry_price * multiplier (default: 1.5x)
✅ Loads API keys + settings from .env
✅ Exits after successful sell
🚨 USE TESTNET ONLY – NOT FOR REAL MONEY
"""

import os
import time
import logging
from dotenv import load_dotenv
import ccxt

# ===========================
# Load ENV CONFIG
# ===========================
load_dotenv()

EXCHANGE_ID = os.getenv("EXCHANGE_ID", "binance")
API_KEY = os.getenv("API_KEY", "")
API_SECRET = os.getenv("API_SECRET", "")
SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
AMOUNT_TO_SELL = float(os.getenv("AMOUNT_TO_SELL", "0.0"))  # 0.0 means auto-sell full balance
ENTRY_PRICE = os.getenv("ENTRY_PRICE")  # required for target calculation
MULTIPLIER = float(os.getenv("MULTIPLIER", "1.5"))  # sell when price >= entry * multiplier
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "5"))

# ===========================
# SETUP LOGGING
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ===========================
# VALIDATIONS
# ===========================
if not API_KEY or not API_SECRET:
    logging.error("❌ Missing API_KEY or API_SECRET in .env")
    raise SystemExit(1)

if not ENTRY_PRICE:
    logging.error("❌ ENTRY_PRICE not set in .env (required to calculate 1.5x target)")
    raise SystemExit(1)

ENTRY_PRICE = float(ENTRY_PRICE)
target_price = ENTRY_PRICE * MULTIPLIER

logging.info("✅ TESTNET BOT STARTED")
logging.info(f"📍 Tracking: {SYMBOL}")
logging.info(f"💵 Entry Price: {ENTRY_PRICE}")
logging.info(f"📈 Target Price ({MULTIPLIER}x): {target_price}")
logging.info(f"⏳ Polling Every: {POLL_INTERVAL} seconds")

# ===========================
# EXCHANGE TESTNET SETUP
# ===========================
exchange_class = getattr(ccxt, EXCHANGE_ID)
exchange = exchange_class({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'},
    'urls': {
        'api': {
            'public': 'https://testnet.binance.vision/api',
            'private': 'https://testnet.binance.vision/api',
        }
    }
})

# ===========================
# FUNCTIONS
# ===========================
def get_ticker_price():
    """Return current market price"""
    ticker = exchange.fetch_ticker(SYMBOL)
    return float(ticker['last'])

def get_balance():
    """Return available coin balance"""
    base_symbol = SYMBOL.split('/')[0]
    bal = exchange.fetch_balance()
    return float(bal['free'].get(base_symbol, 0.0))

def place_market_sell(amount):
    """Place market sell order"""
    try:
        logging.info(f"🚨 Placing sell order for {amount} {SYMBOL.split('/')[0]}")
        order = exchange.create_market_sell_order(SYMBOL, amount)
        logging.info(f"✅ ORDER SUCCESS: {order}")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to sell: {e}")
        return False

# ===========================
# MAIN LOOP
# ===========================
while True:
    try:
        current_price = get_ticker_price()
        logging.info(f"💹 Current Price: {current_price:.2f} | 🎯 Target: {target_price:.2f}")

        if current_price >= target_price:
            logging.info("✅ Target reached! Checking balance...")
            balance = get_balance()

            if AMOUNT_TO_SELL > 0:
                sell_amount = AMOUNT_TO_SELL
            else:
                sell_amount = balance  # sell full balance if no amount specified

            if sell_amount <= 0:
                logging.error("❌ No balance available to sell!")
                break

            success = place_market_sell(sell_amount)
            if success:
                logging.info("🎉 Sell complete. Exiting bot!")
                break

    except ccxt.AuthenticationError:
        logging.error("❌ Authentication error. Check TESTNET API keys.")
        break
    except Exception as e:
        logging.error(f"⚠️ Error: {e}")

    time.sleep(POLL_INTERVAL)