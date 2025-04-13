document.addEventListener("DOMContentLoaded", () => {
  const API_BASE = window.API_BASE || "http://backend:5000";

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
  const startStopButton = document.getElementById("startStopButton");
  const statusDiv = document.getElementById("status");
  const balanceDiv = document.getElementById("balance");

  let chart;
  let socket;

  function showToast(message, type = "info") {
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

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

  async function fetchPrice() {
    try {
      const res = await fetch(`${API_BASE}/api/market_data`);
      const data = await res.json();
      if (data.price) {
        priceElement.textContent = `$${parseFloat(data.price).toFixed(2)}`;
      } else {
        priceElement.textContent = "Error";
      }
    } catch {
      priceElement.textContent = "Error";
    }
  }

  async function fetchBalance() {
    try {
      const res = await fetch(`${API_BASE}/api/balance`);
      const data = await res.json();
      const balanceEl = document.getElementById("balance-display");
      if (balanceEl) {
        balanceEl.textContent = `Balance (${data.account}): $${data.balance.toFixed(2)}`;
      }
      if (balanceDiv) {
        balanceDiv.innerHTML = `USDT Balance: ${data.usdt_balance}`;
      }
    } catch (err) {
      console.error("Balance fetch failed", err);
    }
  }

  async function loadMemory() {
    const res = await fetch(`${API_BASE}/api/memory`);
    const data = await res.json();
    chatBox.innerHTML = "";
    data.forEach((entry) => {
      appendChatMessage("You", entry.user);
      appendChatMessage("AI", entry.ai);
    });
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    appendChatMessage("You", msg);
    chatInput.value = "";

    const res = await fetch(`${API_BASE}/api/ai/chat`, {
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

  function initializeWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${protocol}://${window.location.hostname}:8443/ws/stream`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log("WebSocket connected.");
    };

    socket.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);

        if (newData.type === "market_update") {
          if (Array.isArray(newData.chart)) updateChart(newData.chart);
          if (newData.latest) updatePrices(newData.latest);
        }

        if (newData.type === "bot_status") {
          statusDiv.textContent = newData.running ? "Bot is running" : "Bot is stopped";
          startStopButton.textContent = newData.running ? "Stop Bot" : "Start Bot";
          balanceDiv.textContent = `Balance: $${parseFloat(newData.balance).toFixed(2)}`;
        }
      } catch (e) {
        console.error("Invalid WebSocket message:", e);
      }
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      showToast("WebSocket error. Retrying...", "error");
    };

    socket.onclose = () => {
      console.warn("WebSocket closed. Reconnecting in 5s...");
      showToast("WebSocket closed. Reconnecting...", "warning");
      setTimeout(initializeWebSocket, 5000);
    };
  }

  startStopButton.addEventListener("click", function () {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "toggle_bot" }));
    } else {
      showToast("WebSocket not connected.", "error");
    }
  });

  function updateChart(chartData) {
    if (!chart) return;

    const symbolMap = {};
    chartData.forEach(({ symbol, time, price }) => {
      if (!symbolMap[symbol]) symbolMap[symbol] = { labels: [], prices: [] };
      symbolMap[symbol].labels.push(time);
      symbolMap[symbol].prices.push(price);
    });

    const labels = symbolMap[Object.keys(symbolMap)[0]].labels;
    chart.data.labels = labels;

    chart.data.datasets = Object.entries(symbolMap).map(([symbol, { prices }], index) => ({
      label: symbol,
      data: prices,
      borderColor: getColor(index),
      backgroundColor: "transparent",
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.3
    }));

    chart.update();
  }

  function getColor(index) {
    const colors = ["#00ffcc", "#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"];
    return colors[index % colors.length];
  }

  function updatePrices(latestData) {
    priceElement.innerHTML = "";
    Object.values(latestData).forEach(({ symbol, price }) => {
      const div = document.createElement("div");
      div.textContent = `${symbol}: $${parseFloat(price).toFixed(2)}`;
      priceElement.appendChild(div);
    });
  }

  async function setupChart() {
    const ctx = document.getElementById("chart-canvas").getContext("2d");
    const res = await fetch(`${API_BASE}/api/ohlcv`);
    const data = await res.json();

    chart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: []
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

    updateChart(data);
    updateChartTheme(savedTheme);
  }

  updateBtn.addEventListener("click", async () => {
    const payload = {
      lstm: parseFloat(lstmInput.value),
      trading_ai: parseFloat(aiInput.value),
      reinforcement: parseFloat(rlInput.value)
    };

    const res = await fetch(`${API_BASE}/api/set_preferences`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    showToast(data.status || "Update failed.", "info");
  });

  async function placeOrder(side) {
    const amount = parseFloat(orderAmountInput.value);
    const type = orderTypeSelect.value;
    if (isNaN(amount)) return showToast("Invalid amount.", "error");

    const res = await fetch(`${API_BASE}/api/place_order`, {
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
  setInterval(fetchBalance, 5000);

  window.addEventListener("resize", () => {
    if (chart) {
      chart.resize();
    }
  });
});