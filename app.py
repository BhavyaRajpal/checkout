from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import razorpay
import uuid

app = Flask(__name__, template_folder="templates")  # Ensure templates folder is used
CORS(app)

# Razorpay API Credentials
razorpay_client = razorpay.Client(auth=("YOUR_RAZORPAY_KEY", "YOUR_RAZORPAY_SECRET"))

# Serve the HTML UI
@app.route('/')
def home():
    return render_template("index.html")  # Your UI file

# Create Razorpay Order API
@app.route('/create-order', methods=['POST'])
def create_order():
    data = request.json
    amount = int(data.get("amount", 0))  # Convert to paisa
    currency = "INR"

    try:
        payment_order = razorpay_client.order.create({
            "amount": amount,
            "currency": currency,
            "payment_capture": 1
        })
        return jsonify(payment_order), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Place Order API
@app.route('/place-order', methods=['POST'])
def place_order():
    data = request.json

    required_fields = ["name", "phone", "street", "city", "state", "postalCode", "paymentMethod"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "All fields are required"}), 400

    if len(data["phone"]) != 10 or len(data["postalCode"]) != 6:
        return jsonify({"error": "Invalid phone or postal code"}), 400

    order_id = "ORD" + str(uuid.uuid4().hex[:8]).upper()

    order = {
        "id": order_id,
        "customerName": data["name"],
        "phone": data["phone"],
        "address": {
            "street": data["street"],
            "city": data["city"],
            "state": data["state"],
            "postalCode": data["postalCode"]
        },
        "paymentMethod": data["paymentMethod"],
        "items": data.get("items", []),
        "totalAmount": data.get("total", 0),
        "status": "Pending"
    }

    return jsonify({"message": "Order placed successfully!", "order": order}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
