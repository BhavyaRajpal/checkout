from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import razorpay
import uuid

app = Flask(__name__)
CORS(app)

# Razorpay API Credentials (Replace with your actual keys)
RAZORPAY_KEY = "YOUR_RAZORPAY_KEY"
RAZORPAY_SECRET = "YOUR_RAZORPAY_SECRET"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))

# In-memory order storage (for testing)
orders = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create-order", methods=["POST"])
def create_order():
    data = request.json
    amount = int(data.get("amount", 0))  # Convert to paisa (₹100 = 10000)

    try:
        payment_order = razorpay_client.order.create({
            "amount": amount,  # Amount in paisa
            "currency": "INR",
            "payment_capture": 1
        })

        return jsonify({
            "order_id": payment_order["id"],
            "amount": amount,
            "currency": "INR",
            "razorpay_key": RAZORPAY_KEY
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/verify-payment", methods=["POST"])
def verify_payment():
    data = request.json
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': data["order_id"],
            'razorpay_payment_id': data["payment_id"],
            'razorpay_signature': data["signature"]
        })
        return jsonify({"message": "Payment verified!"}), 200
    except razorpay.errors.SignatureVerificationError:
        return jsonify({"error": "Payment verification failed"}), 400

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
