let chart;
let chartData = {
  labels: [],
  datasets: [{
    label: 'BTC Price (USDT)',
    borderColor: 'rgba(0,255,132,1)',
    backgroundColor: 'rgba(0,255,132,0.2)',
    data: [],
    tension: 0.3
  }]
};

function initChart() {
  const ctx = document.getElementById('chart-canvas').getContext('2d');
  chart = new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
      scales: {
        x: { type: 'time', time: { unit: 'minute' }, title: { display: true, text: 'Time' }},
        y: { title: { display: true, text: 'Price (USDT)' }}
      }
    }
  });
}

async function updateChart() {
  try {
    const res = await fetch('/api/market_data');
    const data = await res.json();
    const now = new Date();
    chartData.labels.push(now);
    chartData.datasets[0].data.push(data.price);
    if (chartData.labels.length > 20) {
      chartData.labels.shift();
      chartData.datasets[0].data.shift();
    }
    chart.update();
    document.getElementById('price').innerText = data.price.toFixed(2);
    document.getElementById('symbol').innerText = data.symbol;
  } catch (err) {
    console.error('Price update failed:', err);
  }
}

async function sendChat(message) {
  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    const data = await res.json();
    const box = document.getElementById('chat-box');
    box.innerHTML += `<div class="user-msg">You: ${message}</div>`;
    box.innerHTML += `<div class="ai-msg">AI: ${data.response}</div>`;
    box.scrollTop = box.scrollHeight;
  } catch (error) {
    console.error('Chat error:', error);
  }
}

async function placeOrder(side) {
  const amount = parseFloat(document.getElementById('order-amount').value);
  const orderType = document.getElementById('order-type').value;
  if (!amount) return alert('Enter amount');

  try {
    const res = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ side, amount, type: orderType })
    });
    const result = await res.json();
    alert(result.status || result.detail || 'Order placed');
  } catch (error) {
    console.error('Order failed:', error);
  }
}

async function emergencyStop() {
  try {
    const res = await fetch('/api/emergency_stop', { method: 'POST' });
    const result = await res.json();
    alert(result.status || 'Emergency stop activated');
  } catch (error) {
    console.error('Emergency stop failed:', error);
  }
}

async function autoTrade() {
  const model = document.getElementById('model-select').value;
  const confidence = parseFloat(document.getElementById('confidence-input').value);

  try {
    const res = await fetch('/api/auto_trade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, confidence_threshold: confidence })
    });
    const result = await res.json();
    alert(`Action: ${result.action.toUpperCase()} at $${result.final_predicted_price}`);
  } catch (err) {
    alert('Auto trading failed.');
    console.error(err);
  }
}

// Event Bindings
document.getElementById('place-buy-order').addEventListener('click', () => placeOrder('buy'));
document.getElementById('place-sell-order').addEventListener('click', () => placeOrder('sell'));
document.getElementById('emergency-stop-btn').addEventListener('click', emergencyStop);
document.getElementById('autoTradeButton').addEventListener('click', autoTrade);
document.getElementById('chat-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const msg = document.getElementById('chat-input').value;
  if (msg.trim()) {
    sendChat(msg);
    document.getElementById('chat-input').value = '';
  }
});
document.getElementById('virtualAccountBtn').addEventListener('click', () => alert("Switched to Virtual Account"));
document.getElementById('realAccountBtn').addEventListener('click', () => alert("Switched to Real Account"));

// Init
initChart();
updateChart();
setInterval(updateChart, 5000);