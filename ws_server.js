const express = require("express");
const http = require("http");
const https = require("https");
const WebSocket = require("ws");
const fetch = require("node-fetch");
const fs = require("fs");
const { execSync } = require("child_process");

const app = express();

// Paths for the certificate and key
const certPath = "certificate.crt";
const keyPath = "private.key";

// Function to check if certificates exist and generate them if not
const generateSelfSignedCerts = () => {
  if (!fs.existsSync(certPath) || !fs.existsSync(keyPath)) {
    console.log("Certificates not found. Generating self-signed certificates...");
    
    // Generate certificates using OpenSSL command
    execSync(`openssl req -nodes -new -x509 -keyout ${keyPath} -out ${certPath} -days 365 -subj "/C=US/ST=State/L=City/O=Company/CN=localhost"`);
    
    console.log("Self-signed certificates generated.");
  } else {
    console.log("Certificates found.");
  }
};

// Generate certificates if they don't exist
generateSelfSignedCerts();

const options = {
  cert: fs.readFileSync(certPath),  // Read the certificate
  key: fs.readFileSync(keyPath),    // Read the private key
};

const server = https.createServer(options, app);
const wss = new WebSocket.Server({ server });

const symbols = ["btcusdt", "ethusdt"];
const binanceURL = `wss://stream.binance.com:9443/stream?streams=${symbols.map(s => `${s}@trade`).join("/")}`;
const BinanceWS = new WebSocket(binanceURL);

let latestData = {};
let chartData = {};  // Collect data for charting

// Store recent history (e.g. last 50 trades)
const maxChartPoints = 50;

BinanceWS.onmessage = async (event) => {
  const stream = JSON.parse(event.data);
  const symbol = stream.stream.split("@")[0];
  const payload = stream.data;

  const price = parseFloat(payload.p);
  const timestamp = new Date().toISOString();

  const formattedSymbol = symbol.toUpperCase();

  const trade = {
    time: timestamp,
    price,
    symbol: formattedSymbol
  };

  latestData[formattedSymbol] = trade;

  // Maintain limited chart history
  if (!chartData[formattedSymbol]) chartData[formattedSymbol] = [];
  chartData[formattedSymbol].push(trade);
  if (chartData[formattedSymbol].length > maxChartPoints) {
    chartData[formattedSymbol].shift();  // Remove oldest
  }

  // Optionally augment with your own backend API data
  try {
    const res = await fetch("http://localhost:5000/api/market_data");
    if (res.ok) {
      const extra = await res.json();
      Object.assign(latestData[formattedSymbol], extra);
    }
  } catch (err) {
    console.warn(`Failed to fetch internal data: ${err.message}`);
  }

  // Broadcast current single latestData and full chartData
  const updatePayload = {
    latest: latestData[formattedSymbol],
    chart: chartData[formattedSymbol]
  };

  const message = JSON.stringify(updatePayload);
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
};

// On new client connection, send current data
wss.on("connection", (ws) => {
  Object.keys(latestData).forEach(symbol => {
    ws.send(JSON.stringify({
      latest: latestData[symbol],
      chart: chartData[symbol] || []
    }));
  });
});

const PORT = process.env.PORT || 8765;
server.listen(PORT, () => {
  console.log(`WebSocket server listening on port ${PORT}`);
});