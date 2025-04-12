const express = require("express");
const http = require("http");
const WebSocket = require("ws");
const fetch = require("node-fetch");

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const symbols = ["btcusdt", "ethusdt"]; // Add more symbols as needed
const binanceURL = `wss://stream.binance.com:9443/stream?streams=${symbols.map(s => `${s}@trade`).join("/")}`;
const BinanceWS = new WebSocket(binanceURL);

let latestData = {};

BinanceWS.onmessage = async (event) => {
  const stream = JSON.parse(event.data);
  const symbol = stream.stream.split("@")[0];
  const payload = stream.data;

  const price = parseFloat(payload.p);
  latestData[symbol.toUpperCase()] = {
    time: new Date().toISOString(),
    price,
    symbol: symbol.toUpperCase()
  };

  // Optionally augment with your own backend API data
  try {
    const res = await fetch("http://localhost:5000/api/market_data");
    if (res.ok) {
      const extra = await res.json();
      Object.assign(latestData[symbol.toUpperCase()], extra);
    }
  } catch (err) {
    console.warn(`Failed to fetch internal data: ${err.message}`);
  }

  // Broadcast update
  const message = JSON.stringify(latestData[symbol.toUpperCase()]);
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
};

wss.on("connection", (ws) => {
  Object.values(latestData).forEach(data => {
    ws.send(JSON.stringify(data));
  });
});

const PORT = process.env.PORT || 8765;
server.listen(PORT, () => {
  console.log(`WebSocket server listening on port ${PORT}`);
});