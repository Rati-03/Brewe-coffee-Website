const ordersContainer = document.querySelector("#orders-container");
const status = document.querySelector("#status");

async function loadOrders() {
    try {
        const response = await fetch("https://brewe-coffee-website-1.onrender.com/orders");

        if (!response.ok) {
            throw new Error("Could not load orders.");
        }

        const orders = await response.json();

        ordersContainer.innerHTML = "";

        if (orders.length === 0) {
            status.textContent = "No orders yet.";
            return;
        }

        status.textContent = `Total orders: ${orders.length}`;

        orders.forEach(function(order) {
            const card = document.createElement("div");
            card.className = "order-card";

            const heading = document.createElement("h3");
            heading.textContent = `Order #${order.id}`;

            const date = document.createElement("p");
            date.textContent = `Date: ${order.created_at}`;
            
            const customer = document.createElement("p");
            customer.textContent = `Customer:${order.customer_name || "not available"}`;

            const phone = document.createElement("p");
            phone.textContent = `Phone:${order.customer_phone|| "not available"}`;
            const list = document.createElement("ul");

            order.items.forEach(function(item) {
                const li = document.createElement("li");
                li.textContent =
                    `${item.name} — ₹${item.price} × ${item.quantity}`;
                list.appendChild(li);
            });

            const total = document.createElement("p");
            total.className = "order-total";
            total.textContent = `Total: ₹${order.total}`;

            card.append(heading, date, customer, phone, list, total);
            ordersContainer.appendChild(card);
        });

    } catch (error) {
        status.textContent =
            "Could not load orders. Check that the Flask backend is running.";
        console.error(error);
    }
}

loadOrders();