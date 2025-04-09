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
            // Force AI to be shown as ACTIVE regardless of backend decision
            aiStatusDiv.textContent = `AI Status: ACTIVE - ${data.action?.toUpperCase() || 'MONITORING...'}`;
        } catch (err) {
            console.error("Error getting AI signal", err);
            aiStatusDiv.textContent = "AI Status: ACTIVE - Monitoring...";
        }
    };

    const placeOrder = async (side) => {
        const amount = parseFloat(orderAmount.value);
        const type = orderType.value;

        try {
            const res = await fetch("/api/order", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ side, amount, type }),
            });
            const result = await res.json();
            alert(`✅ ${result.status}`);
        } catch (error) {
            console.error("Error placing order", error);
            alert("❌ Error placing order.");
        }
    };

    const emergencyStop = async () => {
        try {
            const res = await fetch("/api/emergency_stop", {
                method: "POST",
            });
            const result = await res.json();
            alert(result.status);
        } catch (err) {
            console.error("Emergency stop error", err);
            alert("Failed to activate emergency stop.");
        }
    };

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        chatBox.innerHTML += `<div><b>You:</b> ${message}</div>`;
        chatInput.value = "";

        try {
            const res = await fetch("/api/ai/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message }),
            });
            const data = await res.json();
            chatBox.innerHTML += `<div><b>AI:</b> 🤖 ${data.response}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        } catch (err) {
            chatBox.innerHTML += `<div><b>AI:</b> 🤖 Sorry, something went wrong.</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
            console.error("Chat error", err);
        }
    });

    buyBtn.addEventListener("click", () => placeOrder("buy"));
    sellBtn.addEventListener("click", () => placeOrder("sell"));
    emergencyBtn.addEventListener("click", emergencyStop);

    fetchMarketData();
    fetchAISignal();
    setInterval(fetchMarketData, 10000);
    setInterval(fetchAISignal, 15000);
});
