document.addEventListener("DOMContentLoaded", () => {
    const symbolDiv = document.getElementById("current-symbol");
    const priceDiv = document.getElementById("current-price");
    const pairDiv = document.getElementById("current-trading-pair");
    const aiStatusDiv = document.getElementById("ai-status");
    const buyBtn = document.getElementById("place-buy-order");
    const sellBtn = document.getElementById("place-sell-order");
    const emergencyBtn = document.getElementById("emergency-stop-btn");
    const orderAmount = document.getElementById("order-amount");
    const orderType = document.getElementById("order-type");
    const chatBox = document.getElementById("chat-box");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");

    const fetchMarketData = async () => {
        try {
            const res = await fetch("/api/market_data");
            const data = await res.json();
            symbolDiv.textContent = `Symbol: ${data.symbol}`;
            priceDiv.textContent = `Price: $${data.price}`;
            pairDiv.textContent = `Pair: ${data.symbol}`;
        } catch (err) {
            console.error("Error fetching market data", err);
        }
    };

    const fetchAISignal = async () => {
        try {
            const res = await fetch("/api/ai/signal?model_type=ai");
            const data = await res.json();
            aiStatusDiv.textContent = `AI Status: ${data.action.toUpperCase()}`;
        } catch (err) {
            console.error("Error getting AI signal", err);
        }
    };

    const placeOrder = async (side) => {
        const amount = parseFloat(orderAmount.value);
        const type = orderType.value;

        // Demo only: Logging instead of real order
        console.log(`Placing ${side.toUpperCase()} order: ${amount} ${type}`);
        alert(`Pretend placing ${side.toUpperCase()} order: ${amount} ${type}`);
    };

    const emergencyStop = () => {
        alert("Emergency stop activated (not yet implemented).");
        // Here you'd add a real backend POST call to pause bot.
    };

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        chatBox.innerHTML += `<div><b>You:</b> ${message}</div>`;
        chatInput.value = "";

        // Placeholder: Simulate response
        setTimeout(() => {
            chatBox.innerHTML += `<div><b>AI:</b> 🤖 Sorry, I don't understand yet.</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 1000);
    });

    buyBtn.addEventListener("click", () => placeOrder("buy"));
    sellBtn.addEventListener("click", () => placeOrder("sell"));
    emergencyBtn.addEventListener("click", emergencyStop);

    // Initial load
    fetchMarketData();
    fetchAISignal();
    setInterval(fetchMarketData, 10000); // refresh every 10s
    setInterval(fetchAISignal, 15000); // refresh every 15s
});
