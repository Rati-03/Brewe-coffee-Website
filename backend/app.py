from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DATABASE = "brewe.db"

# Trusted menu prices: the server controls these values.
MENU_PRICES = {
    "Cafe Latte": 145,
    "Cappuccino": 185,
    "Espresspo": 210,
    "Mocha": 240,
    "Cold Cofee": 230,
    "Americano": 260
}

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)
    # Add customer details columns to existing orders table
    columns = [
        row["name"]
        for row in conn.execute("PRAGMA table_info(orders)").fetchall()
    ]

    if "customer_name" not in columns:
        conn.execute("ALTER TABLE orders ADD COLUMN customer_name TEXT")

    if "customer_phone" not in columns:
        conn.execute("ALTER TABLE orders ADD COLUMN customer_phone TEXT")
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return "Welcome to Brewé Coffee Backend!"


@app.route("/contact", methods=["POST"])
def contact():
    fname = request.form.get("fname", "").strip()
    email = request.form.get("email", "").strip()
    subject = request.form.get("sub", "").strip()
    message = request.form.get("message", "").strip()

    if not all([fname, email, subject, message]):
        return "Please fill in all fields.", 400

    conn = get_db_connection()
    conn.execute(
        """INSERT INTO contacts (fname, email, subject, message)
           VALUES (?, ?, ?, ?)""",
        (fname, email, subject, message)
    )
    conn.commit()
    conn.close()

    return "Thank you! Your message has been saved."


@app.route("/orders", methods=["POST"])
def place_order():
    data = request.get_json(silent=True)
    customer_name = data.get("customer_name", "").strip() if isinstance(data, dict) else ""
    customer_phone = data.get("customer_phone", "").strip() if isinstance(data, dict) else ""

    if not customer_name or not customer_phone:
      return jsonify({"error": "Name and phone number are required."}), 400

    if len(customer_name) > 100:
        return jsonify({"error": "Name is too long."}), 400

    if not (
        len(customer_phone) == 10
        and customer_phone.isdigit()
        and customer_phone[0] in "6789"
    ):
        return jsonify({"error": "Enter a valid 10-digit mobile number."}), 400
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return jsonify({"error": "Invalid order data."}), 400

    items = data["items"]

    if not items:
        return jsonify({"error": "Your cart is empty."}), 400

    clean_items = []

    for item in items:
        if not isinstance(item, dict):
            return jsonify({"error": "Invalid item."}), 400

        name = item.get("name")
        quantity = item.get("quantity")

        if (
                not isinstance(name, str)
                or name not in MENU_PRICES
                or isinstance(quantity, bool)
                or not isinstance(quantity, int)
                or quantity < 1
                or quantity > 50
            ):
                return jsonify({"error": "Invalid coffee or quantity."}), 400

            # Always take the price from the trusted server menu.
        clean_items.append({
                "name": name,
                "price": MENU_PRICES[name],
                "quantity": quantity
            })

    # Calculate the total on the backend.
    total = sum(
        item["price"] * item["quantity"] for item in clean_items
    )

    conn = get_db_connection()

    try:
        cursor = conn.execute(
            "INSERT INTO orders (total,customer_name,customer_phone) VALUES (?,?,?)",
            (total, customer_name, customer_phone)
            
        )
        order_id = cursor.lastrowid

        for item in clean_items:
            conn.execute(
                """INSERT INTO order_items
                   (order_id, name, price, quantity)
                   VALUES (?, ?, ?, ?)""",
                (
                    order_id,
                    item["name"],
                    item["price"],
                    item["quantity"]
                )
            )

        conn.commit()

    except Exception:
        conn.rollback()
        app.logger.exception("Could not save order")
        return jsonify({"error": "Could not save your order."}), 500

    finally:
        conn.close()

    return jsonify({
        "message": f"Order #{order_id} placed successfully!",
        "order_id": order_id,
        "total": total
    }), 201
@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_db_connection()

    orders = conn.execute("""
        SELECT
            o.id,
            o.total,
            o.created_at,
            o.customer_name,
            o.customer_phone,
            i.name,
            i.price,
            i.quantity
        FROM orders o
        JOIN order_items i ON o.id = i.order_id
        ORDER BY o.id DESC
    """).fetchall()

    conn.close()

    result = {}

    for row in orders:
        order_id = row["id"]

        if order_id not in result:
            result[order_id] = {
                "id": order_id,
                "total": row["total"],
                "created_at": row["created_at"],
                "customer_name": row["customer_name"],
                "customer_phone": row["customer_phone"],
                "items": []
            }

        result[order_id]["items"].append({
            "name": row["name"],
            "price": row["price"],
            "quantity": row["quantity"]
            
        })

    return jsonify(list(result.values()))

if __name__ == "__main__":
    create_tables()
    app.run(debug=True)