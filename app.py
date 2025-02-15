from flask import Flask, request, jsonify
import json
from decimal import Decimal

app = Flask(__name__)

def calculate_arb_price(sqrt_price_x96):
    """ Convert sqrtPriceX96 to ARB/USD price """
    try:
        sqrt_price_decimal = Decimal(sqrt_price_x96) / (2 ** 96)
        price = sqrt_price_decimal ** 2
        adjusted_price = price / Decimal(10 ** 12)  # Adjust for ARB (18 decimals) vs. USDC (6 decimals)
        return float(adjusted_price)
    except Exception as e:
        print(f"Error in price calculation: {e}")
        return None

@app.route('/moralis-webhook', methods=['POST'])
def moralis_webhook():
    data = request.json
    if data:
        print("✅ Received webhook event")
        print("📜 Full Payload:\n", json.dumps(data, indent=2))  # Pretty print full data

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

