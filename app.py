import os
from decimal import Decimal, getcontext
from flask import Flask, request, jsonify

app = Flask(__name__)

getcontext().prec = 40  # High precision

def calculate_arb_price(sqrt_price_x96):
    try:
        sqrt_price_decimal = Decimal(sqrt_price_x96) / (2 ** 96)
        price = sqrt_price_decimal ** 2
        adjusted_price = price * Decimal(10 ** 12)
        return float(adjusted_price)
    except Exception as e:
        print(f"Error in price calculation: {e}")
        return None

@app.route("/moralis-webhook", methods=["POST"])
def moralis_webhook():
    try:
        data = request.json  # Get Moralis webhook payload
        print("Received webhook data:", data)  # Debugging

        if "logs" in data:
            for log in data["logs"]:
                print("Log data:", log)  # Debug each log entry

                # Extract sqrtPriceX96 from log["data"]
                raw_data = log["data"]
                sqrt_price_x96 = int(raw_data[:66], 16)  # First 66 chars = sqrtPriceX96

                print(f"Extracted sqrtPriceX96: {sqrt_price_x96}")

                arb_price_usd = calculate_arb_price(sqrt_price_x96)
                print(f"Corrected ARB Price in USD: ${arb_price_usd}")

    except Exception as e:
        print(f"Error processing webhook: {e}")

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

