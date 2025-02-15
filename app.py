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

        # Extract Swap Logs
        try:
            logs = data["event"]["data"]["block"]["logs"]
            for log in logs:
                if "topics" in log and log["topics"][0] == "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67":
                    print("🔥 Swap event detected!")

                    transaction_hash = log["transaction"]["hash"]
                    sender = log["transaction"]["from"]["address"]
                    recipient = log["transaction"]["to"]["address"]

                    # Extract sqrtPriceX96 (it's inside 'data' in the log)
                    sqrt_price_x96 = int(log.get("data", "0"), 16)  # Convert hex to int

                    # Calculate ARB/USD Price
                    price_usd = calculate_arb_price(sqrt_price_x96)

                    print(f"🔹 TX: {transaction_hash}")
                    print(f"🔹 Sender: {sender}")
                    print(f"🔹 Recipient: {recipient}")
                    print(f"💰 ARB/USD Price: ${price_usd}")

        except Exception as e:
            print(f"⚠️ Error processing swap: {e}")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

