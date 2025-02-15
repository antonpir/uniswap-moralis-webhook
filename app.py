import os
from decimal import Decimal, getcontext
from flask import Flask, request, jsonify

app = Flask(__name__)

getcontext().prec = 40  # High precision

def calculate_arb_price(sqrt_price_x96):
    try:
        # Convert sqrtPriceX96 to a decimal
        sqrt_price_decimal = Decimal(sqrt_price_x96) / (2 ** 96)

        # Square it to get the raw price ratio (Price of Token0 in Token1)
        price = sqrt_price_decimal ** 2

        # Adjust for decimals: ARB (18) - USDC (6) → 10^(18 - 6) = 10^12
        adjusted_price = price / Decimal(10 ** 12)

        return float(adjusted_price)  # Convert Decimal to float for display
    except Exception as e:
        print(f"Error in price calculation: {e}")
        return None

@app.route("/moralis-webhook", methods=["POST"])
def moralis_webhook():
    try:
        data = request.json  # Get Moralis webhook payload
        print("Received webhook data:", data)  # Debugging

        sqrt_price_x96 = None

        # Try to extract from logs
        if "logs" in data and len(data["logs"]) > 0:
            for log in data["logs"]:
                print("Log data:", log)  # Debug each log entry
                raw_data = log.get("data", "")
                sqrt_price_x96 = int(raw_data[:66], 16)  # First 66 chars = sqrtPriceX96
                break  # Only process the first log entry

        # If logs are empty, extract sqrtPriceX96 from txs input
        if sqrt_price_x96 is None and "txs" in data:
            for tx in data["txs"]:
                input_data = tx.get("input", "")
                if len(input_data) > 66:
                    sqrt_price_x96 = int(input_data[:66], 16)
                    break  # Only process first tx

        if sqrt_price_x96:
            print(f"Extracted sqrtPriceX96: {sqrt_price_x96}")
            arb_price_usd = calculate_arb_price(sqrt_price_x96)
            print(f"Corrected ARB Price in USD: ${arb_price_usd}")
        else:
            print("Could not extract sqrtPriceX96.")

    except Exception as e:
        print(f"Error processing webhook: {e}")

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

