document.addEventListener("DOMContentLoaded", () => {
  const priceElement = document.getElementById("price");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatBox = document.getElementById("chat-box");
  const autoTradeBtn = document.getElementById("autoTradeButton");
  const modelSelect = document.getElementById("model-select");
  const confidenceInput = document.getElementById("confidence-input");
  const emergencyBtn = document.getElementById("emergency-stop-btn");
  const buyBtn = document.getElementById("place-buy-order");
  const sellBtn = document.getElementById("place-sell-order");

  const orderAmountInput = document.getElementById("order-amount");
  const orderTypeSelect = document.getElementById("order-type");

  // Fetch and display current price
  async function fetchPrice() {
    try {
      const res = await fetch("/api/market_data");
      const data = await res.json();
      priceElement.textContent = parseFloat(data.price).toFixed(2);
    } catch (err) {
      priceElement.textContent = "Error";
      console.error("Error fetching market data:", err);
    }
  }

  // AI Chat
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    appendChatMessage("You", userMessage);
    chatInput.value = "";

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });
      const data = await res.json();
      appendChatMessage("AI", data.response);
    } catch (err) {
      appendChatMessage("AI", "Sorry, something went wrong.");
      console.error(err);
    }
  });

  function appendChatMessage(sender, message) {
    const msgEl = document.createElement("div");
    msgEl.className = "chat-message";
    msgEl.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(msgEl);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Auto trade
  autoTradeBtn.addEventListener("click", async () => {
    const model = modelSelect.value;
    const confidence = confidenceInput.value;

    try {
      const res = await fetch("/api/auto_trade", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model, confidence_threshold: confidence }),
      });
      const result = await res.json();
      alert(`Action: ${result.action.toUpperCase()} — Prediction: ${result.final_predicted_price}`);
    } catch (err) {
      alert("Auto trade failed.");
      console.error(err);
    }
  });

  // Emergency stop
  emergencyBtn.addEventListener("click", async () => {
    try {
      const res = await fetch("/api/emergency_stop", { method: "POST" });
      const result = await res.json();
      alert(result.status);
    } catch (err) {
      alert("Failed to trigger emergency stop.");
      console.error(err);
    }
  });

  // Buy/Sell Orders
  async function placeOrder(side) {
    const amount = orderAmountInput.value;
    const type = orderTypeSelect.value;

    if (!amount) return alert("Please enter an order amount.");

    try {
      const res = await fetch("/api/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ side, amount, type }),
      });
      const result = await res.json();
      alert(`${side.toUpperCase()} order executed: ${JSON.stringify(result.order)}`);
    } catch (err) {
      alert("Order failed.");
      console.error(err);
    }
  }

  buyBtn.addEventListener("click", () => placeOrder("buy"));
  sellBtn.addEventListener("click", () => placeOrder("sell"));

  fetchPrice();
  setInterval(fetchPrice, 10000); // refresh price every 10 seconds
});