from web3 import Web3
from decimal import Decimal, getcontext
import json

# ✅ Connect to Alchemy WebSocket
ALCHEMY_WEBSOCKET = "wss://arb-mainnet.g.alchemy.com/v2/ubXirrpIlws_G3ujTpCgFE5uIHv0hQFh"
web3 = Web3(Web3.LegacyWebSocketProvider(ALCHEMY_WEBSOCKET))

getcontext().prec = 40  # High precision calculations

# ✅ Uniswap V3 Swap Event ABI
SWAP_EVENT_ABI = json.loads("""
[
    {
        "anonymous": false,
        "inputs": [
            {"indexed": true, "internalType": "address", "name": "sender", "type": "address"},
            {"indexed": true, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": false, "internalType": "int256", "name": "amount0", "type": "int256"},
            {"indexed": false, "internalType": "int256", "name": "amount1", "type": "int256"},
            {"indexed": false, "internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"indexed": false, "internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"indexed": false, "internalType": "int24", "name": "tick", "type": "int24"}
        ],
        "name": "Swap",
        "type": "event"
    }
]
""")

# ✅ ARB/USDC Uniswap V3 Pool Address
UNISWAP_V3_POOL_ADDRESS = Web3.to_checksum_address("0xb0f6cA40411360c03d41C5fFc5F179b8403CdcF8")

def handle_swap_event(event):
    sqrt_price_x96 = event["args"]["sqrtPriceX96"]
    price = calculate_arb_price(sqrt_price_x96)
    print(f"🔥 Real-time ARB Price in USD: ${price}")

def calculate_arb_price(sqrt_price_x96):
    try:
        sqrt_price_decimal = Decimal(sqrt_price_x96) / (2 ** 96)
        price = sqrt_price_decimal ** 2
        adjusted_price = price / Decimal(10 ** 12)  # Adjust decimals (ARB 18 → USDC 6)
        return float(adjusted_price)
    except Exception as e:
        print(f"Error in price calculation: {e}")
        return None

def main():
    print("🔗 Listening to Uniswap V3 Swap Events...")
    event_filter = web3.eth.filter({
        "address": UNISWAP_V3_POOL_ADDRESS,
        "topics": [web3.keccak(text="Swap(address,address,int256,int256,uint160,uint128,int24)").hex()]
    })
    while True:
        for event in event_filter.get_new_entries():
            handle_swap_event(web3.eth.contract(address=UNISWAP_V3_POOL_ADDRESS, abi=SWAP_EVENT_ABI).events.Swap().processLog(event))

if __name__ == "__main__":
    main()

