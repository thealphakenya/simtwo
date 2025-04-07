// Trading Algorithm Control
class TradingController {
    constructor() {
        this.aggressiveness = 3;
        this.stopLoss = 5;
        this.trailingStop = 'none';
        this.tradingHours = {
            enabled: false,
            start: '09:30',
            end: '16:00',
            days: [1, 2, 3, 4, 5]  // Weekdays
        };
        this.loadSettings();
    }

    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('tradingSettings')) || {};
        if (settings.aggressiveness) this.aggressiveness = settings.aggressiveness;
        if (settings.stopLoss) this.stopLoss = settings.stopLoss;
        if (settings.trailingStop) this.trailingStop = settings.trailingStop;
        if (settings.tradingHours) this.tradingHours = settings.tradingHours;
    }

    async executeTrade(symbol, amount, action) {
        showOrderNotification('processing', `Processing ${action} order...`);
        
        try {
            const response = await fetch('/api/trade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Account-Type': currentAccount.type
                },
                body: JSON.stringify({ symbol, amount, action })
            });
            
            const result = await response.json();
            showOrderNotification('success', `${action.toUpperCase()} order executed successfully`);
            return result;
        } catch (error) {
            showOrderNotification('error', `Failed to execute ${action} order`);
            console.error('Trade error:', error);
        }
    }
}

// Advanced Animation Controller
class AnimationController {
    static priceChange(element, newValue, oldValue) {
        element.classList.remove('price-up', 'price-down');
        void element.offsetWidth;  // Trigger reflow
        
        if (newValue > oldValue) {
            element.classList.add('price-up');
        } else if (newValue < oldValue) {
            element.classList.add('price-down');
        }
    }

    static async typewriterEffect(element, text, speed = 30) {
        element.textContent = '';
        for (let i = 0; i < text.length; i++) {
            element.textContent += text.charAt(i);
            await new Promise(resolve => setTimeout(resolve, speed));
        }
    }
}

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    const tradingCtrl = new TradingController();
    window.tradingCtrl = tradingCtrl;
    
    // Load market data with animation
    loadMarketDataWithAnimation();
    
    // Set up all event listeners
    initEventListeners();
});

async function loadMarketDataWithAnimation() {
    const container = document.getElementById('market-data-container');
    container.innerHTML = '<div class="crypto-pulse-loader"></div>';
    
    try {
        const response = await fetch('/api/market-data');
        const data = await response.json();
        renderMarketData(data);
    } catch (error) {
        container.innerHTML = '<div class="error-animation">Failed to load data</div>';
    }
}