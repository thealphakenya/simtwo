document.addEventListener("DOMContentLoaded", async () => {
    const loadingScreen = document.getElementById("loading-screen");
    const mainContent = document.getElementById("main-content");
    const currentPriceEl = document.getElementById("current-price");
    const chartCanvas = document.getElementById("chart-canvas");
    const aiStatus = document.getElementById("ai-status");

    let chart;

    // Utility: Fetch market price
    async function fetchPrice() {
        try {
            const response = await fetch("/api/market_data");
            const data = await response.json();
            const price = parseFloat(data.price).toFixed(2);
            currentPriceEl.textContent = `$${price}`;
        } catch (err) {
            currentPriceEl.textContent = "Error";
            console.error("Market data fetch error:", err);
        }
    }

    // Utility: Fetch AI signal
    async function fetchAISignal() {
        try {
            const response = await fetch("/api/ai/signal");
            const data = await response.json();
            const signal = data.action.toUpperCase();
            aiStatus.textContent = `AI: ${signal}`;
            aiStatus.classList.remove("bg-green-100", "bg-yellow-100", "bg-red-100");

            switch (signal) {
                case "BUY":
                    aiStatus.classList.add("bg-green-100", "text-green-800");
                    break;
                case "SELL":
                    aiStatus.classList.add("bg-red-100", "text-red-800");
                    break;
                default:
                    aiStatus.classList.add("bg-yellow-100", "text-yellow-800");
            }
        } catch (err) {
            aiStatus.textContent = "AI: ERROR";
            console.error("AI signal fetch error:", err);
        }
    }

    // Utility: Render dummy chart for now
    function renderChart() {
        chart = new Chart(chartCanvas, {
            type: "line",
            data: {
                labels: Array.from({ length: 60 }, (_, i) => i),
                datasets: [{
                    label: "Price",
                    data: Array.from({ length: 60 }, () => 50000 + Math.random() * 500),
                    borderColor: "#3B82F6",
                    backgroundColor: "rgba(59, 130, 246, 0.1)",
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                animation: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: { display: false },
                    y: { ticks: { callback: value => `$${value}` } }
                }
            }
        });
    }

    // Event: Buy/Sell Button Click
    document.getElementById("place-buy-order").addEventListener("click", () => {
        const amount = document.getElementById("order-amount").value;
        console.log(`Placing BUY order for ${amount}`);
        alert(`🔼 BUY order placed for ${amount}`);
        // Optional: POST to your backend to trigger order
    });

    document.getElementById("place-sell-order").addEventListener("click", () => {
        const amount = document.getElementById("order-amount").value;
        console.log(`Placing SELL order for ${amount}`);
        alert(`🔽 SELL order placed for ${amount}`);
        // Optional: POST to your backend to trigger order
    });

    // Event: Emergency Stop
    document.getElementById("emergency-stop-btn").addEventListener("click", () => {
        console.warn("🛑 EMERGENCY STOP triggered!");
        alert("🛑 Emergency stop activated! All trading halted.");
        // Optional: POST to backend to disable trading
    });

    // Load & display
    await fetchPrice();
    await fetchAISignal();
    renderChart();

    // Hide loading screen after init
    loadingScreen.classList.add("hidden");
    mainContent.classList.remove("hidden");

    // Refresh every 10 seconds
    setInterval(() => {
        fetchPrice();
        fetchAISignal();
        if (chart) {
            const newPrice = 50000 + Math.random() * 500;
            chart.data.datasets[0].data.shift();
            chart.data.datasets[0].data.push(newPrice);
            chart.update();
        }
    }, 10000);
});
