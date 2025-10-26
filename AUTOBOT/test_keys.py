import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

exchange = ccxt.binance({
    'apiKey': os.getenv("API_KEY"),
    'secret': os.getenv("API_SECRET"),
    'enableRateLimit': True,
    'options': {
        'defaultType': 'spot',
    },
    'urls': {
        'api': {
            'public': 'https://testnet.binance.vision/api',
            'private': 'https://testnet.binance.vision/sapi',  # ✅ Fix here
        }
    }
})

try:
    balance = exchange.fetch_balance()
    print("✅ Authentication Success! Balance:", balance['total'])
except Exception as e:
    print("❌ Authentication Failed:", e)