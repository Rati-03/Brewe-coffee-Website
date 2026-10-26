const checkoutItems = document.querySelector("#checkout-items");
const checkoutTotal = document.querySelector("#checkout-total");
const checkoutForm = document.querySelector("#checkout-form");
const orderMessage = document.querySelector("#order-message");
const placeOrderButton = document.querySelector("#place-order");

const cart = JSON.parse(sessionStorage.getItem("breweCart")) || [];

function renderCheckout() {
    checkoutItems.innerHTML = "";
    let total = 0;

    cart.forEach(function(item) {
        total += item.price * item.quantity;

        const li = document.createElement("li");
        li.textContent =
            `${item.name} — ₹${item.price} × ${item.quantity}`;

        checkoutItems.appendChild(li);
    });

    checkoutTotal.textContent = total;

    if (cart.length === 0) {
        checkoutItems.innerHTML = "<li>Your cart is empty.</li>";
    }
}

renderCheckout();

checkoutForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    if (cart.length === 0) {
        orderMessage.textContent = "Your cart is empty. Please add coffee first.";
        return;
    }

    const customerName =
        document.querySelector("#customer-name").value.trim();

    const customerPhone =
        document.querySelector("#customer-phone").value.trim();

    const order = {
        customer_name: customerName,
        customer_phone: customerPhone,
        items: cart.map(function(item) {
            return {
                name: item.name,
                quantity: item.quantity
            };
        })
    };

    try {
        placeOrderButton.disabled = true;
        orderMessage.textContent = "Placing your order...";

        const response = await fetch("https://brewe-coffee-website-1.onrender.com/orders", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(order)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Order failed.");
        }

        orderMessage.textContent =
            `${result.message} Total: ₹${result.total}`;

        sessionStorage.removeItem("breweCart");
        checkoutForm.reset();
        cart.length = 0;
        // renderCheckout();

    } catch (error) {
        orderMessage.textContent =
            "Could not place order. Make sure the backend is running.";
        console.error(error);
    } finally {
        placeOrderButton.disabled = false;
    }
});