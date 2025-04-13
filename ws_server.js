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
  const lstmInput = document.getElementById("lstm-weight");
  const aiInput = document.getElementById("trading-ai-weight");
  const rlInput = document.getElementById("reinforcement-weight");
  const updateBtn = document.getElementById("update-strategy");
  const aiStatusIndicator = document.getElementById("ai-status-indicator");
  const themeToggle = document.getElementById("theme-toggle");
  const themeLabel = document.getElementById("theme-label");
  const symbolSelect = document.getElementById("symbol-select");

  let chart;
  let socket;
  let activeSymbol = symbolSelect.value;

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
      const res = await fetch("/api/market_data");
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

  async function loadMemory() {
    try {
      const res = await fetch("/api/memory");
      const data = await res.json();
      chatBox.innerHTML = "";
      data.forEach((entry) => {
        appendChatMessage("You", entry.user);
        appendChatMessage("AI", entry.ai);
      });
    } catch (err) {
      console.error("Failed to load memory", err);
    }
  }

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    appendChatMessage("You", msg);
    chatInput.value = "";

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      appendChatMessage("AI", data.response || "Error");
      loadMemory();
    } catch (err) {
      console.error("Chat request failed", err);
      appendChatMessage("AI", "Error");
    }
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
    const wsUrl = `${protocol}://${window.location.host}/ws/stream`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log("WebSocket connected.");
    };

    socket.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);

        if (Array.isArray(newData.chart)) {
          updateChart(newData.chart);
        }

        if (newData.latest) {
          updatePrices(newData.latest);
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

  function updateChart(chartData) {
    if (!chart) return;

    const symbolMap = {};
    chartData.forEach(({ symbol, time, price }) => {
      if (!symbolMap[symbol]) symbolMap[symbol] = { labels: [], prices: [] };
      symbolMap[symbol].labels.push(time);
      symbolMap[symbol].prices.push(price);
    });

    const labels = symbolMap[Object.keys(symbolMap)[00