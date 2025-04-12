document.addEventListener("DOMContentLoaded", () => {
  const preferencesForm = document.getElementById("preferences-form");
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
  const lstmInput = document.getElementById("lstm-weight");
  const aiInput = document.getElementById("trading-ai-weight");
  const rlInput = document.getElementById("reinforcement-weight");
  const updateBtn = document.getElementById("update-strategy");
  const aiStatusIndicator = document.getElementById("ai-status-indicator");
  const themeToggle = document.getElementById("theme-toggle");
  const themeLabel = document.getElementById("theme-label");

  let chart;
  let socket;

  // Toast utility
  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  // Theme toggle handling
  const savedTheme = localStorage.getItem("theme") || "dark";
  document.body.classList.add(savedTheme);
  themeToggle.checked = savedTheme === "light";
  themeLabel.textContent = savedTheme === "light" ? "Light Mode" : "Dark Mode";

  themeToggle.addEventListener("change", () => {
    document.body.classList.toggle("dark");
    document.body.classList.toggle("light");

    const newTheme = document.body.classList.contains("light") ? "light" : "dark";
    localStorage.setItem("theme", newTheme);
    themeLabel.textContent = newTheme === "light" ? "Light Mode" : "Dark Mode";

    updateChartTheme(newTheme);
  });

  // Update chart styling based on theme
  function updateChartTheme(theme) {
    const isDark = theme === "dark";
    const gridColor = isDark ? "#333" : "#ccc";
    const textColor = isDark ? "#eee" : "#111";

    if (chart) {
      chart.options.scales.x.ticks.color = textColor;
      chart.options.scales.y.ticks.color = textColor;
      chart.options.scales.x.grid.color = gridColor;
      chart.options.scales.y.grid.color = gridColor;
      chart.options.plugins.legend.labels.color = textColor;
      chart.update();
    }
  }

  // Fetch market price
  async function fetchPrice() {
    try {
      const res = await fetch("/api/market_data");
      const data = await res.json();
      priceElement.textContent = data.price ? parseFloat(data.price).toFixed(2) : "Error";
    } catch {
      priceElement.textContent = "Error";
    }
  }

  // Fetch balance
  async function fetchBalance() {
    try {
      const res = await fetch("/api/balance");
      const data = await res.json();
      const balanceEl = document.getElementById("balance-display");
      if (balanceEl) {
        balanceEl.textContent = `Balance (${data.account}): $${data.balance.toFixed(2)}`;
      }
    } catch (err) {
      console.error("Balance fetch failed", err);
    }
  }

  // Fetch chat memory
  async function loadMemory() {
    const res = await fetch("/api/memory");
    const data = await res.json();
    chatBox.innerHTML = "";
    data.forEach((entry) => {
      appendChatMessage("You", entry.user);
      appendChatMessage("AI", entry.ai);
    });
  }

  // Chat message handling
  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    appendChatMessage("You", msg);
    chatInput.value = "";

    const res = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg })
    });

    const data = await res.json();
    appendChatMessage("AI", data.response || "Error");
    loadMemory();
  });

  function appendChatMessage(sender, message) {
    const el = document.createElement("div");
    el.className = "chat-message";
    el.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(el);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // WebSocket for real-time data updates
  function initializeWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log("WebSocket connected.");
    };

    socket.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        updateChart(newData);
      } catch (e) {
        console.error("Invalid WebSocket message:", e);
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    socket.onclose = () => {
      console.warn("WebSocket closed. Reconnecting in 5s...");
      setTimeout(initializeWebSocket, 5000);
    };
  }

  // Chart setup
  async function setupChart() {
    const ctx = document.getElementById("chart-canvas").getContext("2d");
    const res = await fetch("/api/chart_data");
    const data = await res.json();

    const labels = data.map(item => item.time);
    const prices = data.map(item => item.price);

    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Price",
          data: prices,
          borderColor: "#00ffcc",
          backgroundColor: "rgba(0,255,204,0.1)",
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { display: true, ticks: { color: "#aaa" } },
          y: { display: true, ticks: { color: "#aaa" } }
        },
        plugins: {
          legend: { labels: { color: "#ccc" } }
        }
      }
    });

    updateChartTheme(savedTheme);
  }

  function updateChart(newData) {
    if (!chart) return;
    chart.data.labels = newData.map(item => item.time);
    chart.data.datasets[0].data = newData.map(item => item.price);
    chart.update();
  }

  // Update strategy weights
  updateBtn.addEventListener("click", async () => {
    const payload = {
      lstm: parseFloat(lstmInput.value),
      trading_ai: parseFloat(aiInput.value),
      reinforcement: parseFloat(rlInput.value)
    };

    const res = await fetch("/api/strategy_weights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    showToast(data.status || "Update failed.", "info");
  });

  // Place order functions
  async function placeOrder(side) {
    const amount = parseFloat(orderAmountInput.value);
    const type = orderTypeSelect.value;
    if (isNaN(amount)) return showToast("Invalid amount.", "error");

    const res = await fetch("/api/order", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ side, amount, type })
    });

    const result = await res.json();
    showToast(result.status || "Error", "info");
  }

  buyBtn.addEventListener("click", () => placeOrder("buy"));
  sellBtn.addEventListener("click", () => placeOrder("sell"));

  fetchPrice();
  fetchBalance();
  loadMemory();
  setupChart();
  initializeWebSocket();

  setInterval(fetchPrice, 10000);
  setInterval(fetchBalance, 15000);
});