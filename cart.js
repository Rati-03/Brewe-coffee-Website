const buttons = document.querySelectorAll(".add-to-cart");
const cartItems = document.querySelector("#cart-items");
const cartTotal = document.querySelector("#cart-total");

const cart = [];

function renderCart() {
    cartItems.innerHTML = "";

    let total = 0;

    cart.forEach(function(item, index) {
        total += item.price * item.quantity;

        const li = document.createElement("li");

        li.textContent =
            `${item.name} - ₹${item.price} × ${item.quantity} `;

        const removeButton = document.createElement("button");
        removeButton.textContent = "Remove";

        removeButton.addEventListener("click", function() {
            cart.splice(index, 1);
            renderCart();
        });

        li.appendChild(removeButton);
        cartItems.appendChild(li);
    });

    cartTotal.textContent = total;
}

buttons.forEach(function(button) {
    button.addEventListener("click", function() {
        const card = button.closest(".card-content");

        const name = card.querySelector("h2").textContent;
        const priceText = card.querySelector("h3").textContent;
        const price = Number(priceText.replace("₹", "").trim());

        const existingItem = cart.find(function(item) {
            return item.name === name;
        });

        if (existingItem) {
            existingItem.quantity++;
        } else {
            cart.push({
                name: name,
                price: price,
                quantity: 1
            });
        }

        renderCart();
    });
});


const placeOrderButton = document.querySelector("#place-order");
const orderMessage = document.querySelector("#order-message");

placeOrderButton.addEventListener("click", function() {
    if (cart.length === 0) {
        orderMessage.textContent = "Please add coffee to your cart first.";
        return;
    }

    sessionStorage.setItem("breweCart", JSON.stringify(cart));

    window.location.href = "checkout.html";
});