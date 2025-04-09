let selectedAccount = "virtual";
let autoTradeButton = document.getElementById("autoTradeButton");
let accountBalance = document.getElementById("balance");
let orderList = document.getElementById("orderList");
let chatMessages = document.getElementById("chat-box");
let chatInput = document.getElementById("chat-input");
let sendChatButton = document.getElementById("send-chat");
let symbolDiv = document.getElementById("current-symbol");
let priceDiv = document.getElementById("current-price");
let pairDiv = document.getElementById("current-trading-pair");
let aiStatusDiv = document.getElementById("ai-status");
let buyBtn = document.getElementById("place-buy-order");
let sellBtn = document.getElementById("place-sell-order");
let emergencyBtn = document.getElementById("emergency-stop-btn");
let orderAmount = document.getElementById("order-amount");
let orderType = document.getElementById("order-type");
let chatForm = document.getElementById("chat-form");

// Loading Spinner Functions
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Fetch Market Data with Loading Spinner
async function fetchMarketData() {
    showLoading();
    try {
        const res = await fetch("/api/market_data");
        const data = await res.json();
        symbolDiv.textContent = `Symbol: ${data.symbol}`;
        priceDiv.textContent = `Price: $${data.price}`;
        pairDiv.textContent = `Pair: ${data.symbol}`;
    } catch (err) {
        console.error("Error fetching market data", err);
    } finally {
        hideLoading();
    }
}

// Fetch AI Signal with Loading Spinner
async function fetchAISignal() {
    showLoading();
    try {
        const res = await fetch("/api/ai/signal?model_type=ai");
        const data = await res.json();
        aiStatusDiv.textContent = `AI Status: ACTIVE - ${data.action?.toUpperCase() || 'MONITORING...'}`;
    } catch (err) {
        console.error("Error getting AI signal", err);
        aiStatusDiv.textContent = "AI Status: ACTIVE - Monitoring...";
    } finally {
        hideLoading();
    }
}

// Update Account Balance
function updateAccountBalance() {
    showLoading();
    fetch("/api/account")
        .then(response => response.json())
        .then(data => {
            selectedAccount = data.account;
            accountBalance.textContent = `Balance: $${data.balance.toFixed(2)}`;
        })
        .finally(() => hideLoading());
}

// Switch Account
function switchAccount(accountType) {
    showLoading();
    fetch("/api/select_account", {
        method: "POST",
        body: JSON.stringify({ account_type: accountType }),
        headers: { "Content-Type": "application/json" }
    }).then(response => response.json())
      .then(data => {
          updateAccountBalance();
      })
      .finally(() => hideLoading());
}

// Start Auto Trading
function startAutoTrading() {
    autoTradeButton.style.backgroundColor = "green";
    autoTradeButton.textContent = "Auto Trading Active";
    setInterval(() => {
        showLoading();
        fetch("/api/order", { 
            method: "POST", 
            body: JSON.stringify({ side: "buy", amount: 0.01 }), 
            headers: { "Content-Type": "application/json" } 
        })
            .then(response => response.json())
            .then(data => {
                let tradeRow = document.createElement("li");
                tradeRow.textContent = `${data.status} - ${selectedAccount} Account`;
                orderList.appendChild(tradeRow);
                updateAccountBalance();
            })
            .finally(() => hideLoading());
    }, 5000); // Auto trading every 5 seconds
}

// Send Chat Message
function sendChatMessage() {
    const message = chatInput.value;
    if (message.trim() === "") return;

    // Display the user's message
    chatMessages.innerHTML += `<div class="user-message">You: ${message}</div>`;

    // Clear the input field
    chatInput.value = '';

    // Send the message to the AI backend
    fetch("/api/ai/chat", {
        method: "POST",
        body: JSON.stringify({ message: message }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        const aiResponse = data.response;
        // Display the AI's response
        chatMessages.innerHTML += `<div class="ai-message">AI: ${aiResponse}</div>`;
        chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to the bottom
    })
    .catch(error => console.error("Error in AI chat:", error));
}

// Place Order
async function placeOrder(side) {
    const amount = parseFloat(orderAmount.value);
    const type = orderType.value;

    showLoading();
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
    } finally {
        hideLoading();
    }
}

// Emergency Stop
async function emergencyStop() {
    showLoading();
    try {
        const res = await fetch("/api/emergency_stop", {
            method: "POST",
        });
        const result = await res.json();
        alert(result.status);
    } catch (err) {
        console.error("Emergency stop error", err);
        alert("Failed to activate emergency stop.");
    } finally {
        hideLoading();
    }
}

// Initialize the dashboard
document.addEventListener("DOMContentLoaded", () => {
    // Initialize balances and symbols on page load
    updateAccountBalance();
    fetchMarketData();
    fetchAISignal();

    // Set intervals for fetching data
    setInterval(fetchMarketData, 10000);  // Refresh market data every 10 seconds
    setInterval(fetchAISignal, 15000);    // Refresh AI status every 15 seconds

    // Event listeners
    document.getElementById("virtualAccountBtn").addEventListener("click", () => switchAccount("virtual"));
    document.getElementById("realAccountBtn").addEventListener("click", () => switchAccount("real"));
    autoTradeButton.addEventListener("click", startAutoTrading);
    buyBtn.addEventListener("click", () => placeOrder("buy"));
    sellBtn.addEventListener("click", () => placeOrder("sell"));
    emergencyBtn.addEventListener("click", emergencyStop);
    
    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        sendChatMessage();
    });
});
