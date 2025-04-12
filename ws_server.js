const express = require("express");
const http = require("http");
const https = require("https");
const WebSocket = require("ws");
const fetch = require("node-fetch");
const fs = require("fs");

const app = express();

// HTTPS cert and key setup
const options = {
  cert: fs.readFileSync("path/to/certificate.crt"), // Replace with actual cert path
  key: fs.readFileSync("path/to/private.key"),       // Replace with actual key path
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