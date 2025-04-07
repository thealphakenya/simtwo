document.addEventListener('DOMContentLoaded', function () {
    const socket = io.connect('http://localhost:5000');  // Connect to the backend socket
    const currentSymbol = document.getElementById('current-symbol');
    const currentPrice = document.getElementById('current-price');
    const currentTradingPair = document.getElementById('current-trading-pair');
    const tradingChart = document.getElementById('chart-canvas');
    const aiStatus = document.getElementById('ai-status');
    const orderType = document.getElementById('order-type');
    const orderAmount = document.getElementById('order-amount');
    const placeBuyOrderBtn = document.getElementById('place-buy-order');
    const placeSellOrderBtn = document.getElementById('place-sell-order');
    const chatInput = document.getElementById('chat-input');
    const emergencyStopBtn = document.getElementById('emergency-stop-btn');
    const aiChatSection = document.getElementById('chatwithai');

    // Initialize the trading chart (using Chart.js)
    let chart = new Chart(tradingChart, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                data: []
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom'
                }
            }
        }
    });

    // Listen for AI status changes from the backend (AI Active or Inactive)
    socket.on('ai_status', function (status) {
        aiStatus.innerText = status === 'active' ? 'AI Active' : 'AI Inactive';
    });

    // Listen for the most recent trading pair
    socket.on('current_pair', function (pair) {
        currentTradingPair.innerText = pair;
        currentSymbol.innerText = pair;
        updateChart(pair);
    });

    // Update chart data when the market data changes
    function updateChart(pair) {
        fetch(`/api/market_data`)
            .then(response => response.json())
            .then(data => {
                const prices = data.prices;  // Assuming prices is an array of [timestamp, price]
                const labels = prices.map(item => item[0]);
                const priceData = prices.map(item => item[1]);

                chart.data.labels = labels;
                chart.data.datasets[0].data = priceData;
                chart.update();
            })
            .catch(err => console.error("Error fetching market data:", err));
    }

    // Place a buy order
    placeBuyOrderBtn.addEventListener('click', function () {
        const amount = orderAmount.value;
        if (amount <= 0) {
            alert('Please enter a valid order amount');
            return;
        }

        const orderDetails = {
            type: orderType.value,
            action: 'buy',
            amount: amount
        };

        socket.emit('place_order', orderDetails);
    });

    // Place a sell order
    placeSellOrderBtn.addEventListener('click', function () {
        const amount = orderAmount.value;
        if (amount <= 0) {
            alert('Please enter a valid order amount');
            return;
        }

        const orderDetails = {
            type: orderType.value,
            action: 'sell',
            amount: amount
        };

        socket.emit('place_order', orderDetails);
    });

    // Emergency stop button to halt trading
    emergencyStopBtn.addEventListener('click', function () {
        socket.emit('emergency_stop', { message: 'Stop Trading' });
    });

    // Chat with AI functionality
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('chat-box');

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const message = chatInput.value;
        if (message.trim() === '') {
            return;
        }

        socket.emit('chat_message', { message: message });

        // Display the message in the chat box
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.innerText = `You: ${message}`;
        chatBox.appendChild(messageElement);

        chatInput.value = '';  // Clear chat input field
    });

    // Listen for AI's response in chat
    socket.on('ai_response', function (response) {
        const responseElement = document.createElement('div');
        responseElement.classList.add('chat-message');
        responseElement.innerText = `AI: ${response}`;
        chatBox.appendChild(responseElement);
    });

    // Periodically request AI status (this can be a more sophisticated request, e.g., on certain events)
    setInterval(function () {
        socket.emit('get_ai_status');
    }, 5000);
});
