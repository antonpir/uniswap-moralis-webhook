import os
from decimal import Decimal, getcontext
from flask import Flask, request, jsonify

getcontext().prec = 40  # Set high precision to avoid overflow

app = Flask(__name__)

# Function to calculate ARB price in USD
def calculate_arb_price(sqrt_price_x96):
    price = (Decimal(sqrt_price_x96) / (2 ** 96)) ** 2
    adjusted_price = price * Decimal(10 ** 12)  # Adjust for ARB (18) → USDC (6)
    return float(adjusted_price)  # Convert Decimal to float

@app.route("/moralis-webhook", methods=["POST"])
def moralis_webhook():
    data = request.json
    if "logs" in data:
        for log in data["logs"]:
            sqrt_price_x96 = int(log["data"][:66], 16)  # Extract sqrtPriceX96 from data field
            arb_price_usd = calculate_arb_price(sqrt_price_x96)
            print(f"ARB Price in USD: ${arb_price_usd}")
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

