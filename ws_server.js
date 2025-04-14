const express = require("express");
const https = require("https");
const WebSocket = require("ws");
const fetch = require("node-fetch");
const fs = require("fs");
const { execSync } = require("child_process");

const app = express();

const certPath = "certificate.crt";
const keyPath = "private.key";

// Function to generate self-signed certificates if they don't exist
const generateSelfSignedCerts = () => {
  if (!fs.existsSync(certPath) || !fs.existsSync(keyPath)) {
    console.log("Certificates not found. Generating self-signed certificates...");
    execSync(`openssl req -nodes -new -x509 -keyout ${keyPath} -out ${certPath} -days 365 -subj "/C=US/ST=State/L=City/O=Company/CN=localhost"`);
    console.log("Self-signed certificates generated.");
  } else {
    console.log("Certificates found.");
  }
};

generateSelfSignedCerts();

const options = {
  cert: fs.readFileSync(certPath),
  key: fs.readFileSync(keyPath),
};

const server = https.createServer(options, app);
const wss = new WebSocket.Server({ server, path: "/ws/stream" });

const symbols = ["btcusdt", "ethusdt"];
const binanceURL = `wss://stream.binance.com:9443/stream?streams=${symbols.map(s => `${s}@trade`).join("/")}`;
const BinanceWS = new WebSocket(binanceURL);

let latestData = {};
let chartData = {};
const maxChartPoints = 50;

// P2P bot state
let botRunning = false;
let botBalance = 0;

// Simulate bot toggle from frontend
wss.on("connection", (ws) => {
  console.log("Client connected to WebSocket.");

  // Send initial P2P bot status
  ws.send(JSON.stringify({
    type: "bot_status",
    running: botRunning,
    balance: botBalance,
  }));

  // Handle messages from the frontend
  ws.on("message", (msg) => {
    try {
      const data = JSON.parse(msg);

      if (data.type === "toggle_bot") {
        botRunning = !botRunning;
        botBalance = Math.random() * 1000; // Simulated new balance

        const update = {
          type: "bot_status",
          running: botRunning,
          balance: botBalance.toFixed(2),
        };

        // Broadcast new status to all connected clients
        wss.clients.forEach(client => {
          if (client.readyState === WebSocket.OPEN) {
            client.send(JSON.stringify(update));
          }
        });

        console.log(`Bot toggled. Running: ${botRunning}, Balance: $${botBalance.toFixed(2)}`);
      }
    } catch (e) {
      console.warn("Invalid WebSocket message:", msg, e);
    }
  });

  // Handle WebSocket client closure
  ws.on("close", () => {
    console.log("Client disconnected from WebSocket.");
  });
});

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

  if (!chartData[formattedSymbol]) chartData[formattedSymbol] = [];
  chartData[formattedSymbol].push(trade);
  if (chartData[formattedSymbol].length > maxChartPoints) {
    chartData[formattedSymbol].shift();
  }

  try {
    const res = await fetch("http://backend:5000/api/market_data");
    if (res.ok) {
      const extra = await res.json();
      Object.assign(latestData[formattedSymbol], extra);
    }
  } catch (err) {
    console.warn(`Failed to fetch internal data: ${err.message}`);
  }

  const updatePayload = {
    type: "market_update",
    latest: latestData[formattedSymbol],
    chart: chartData[formattedSymbol]
  };

  const message = JSON.stringify(updatePayload);
  // Broadcast market update to all WebSocket clients
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
};

// Start the server on HTTPS port 8443
server.listen(8443, () => {
  console.log("Server listening on https://localhost:8443");
});

// Graceful shutdown handling
process.on("SIGINT", () => {
  console.log("Shutting down server...");
  server.close(() => {
    console.log("Server closed.");
    process.exit(0);
  });
});