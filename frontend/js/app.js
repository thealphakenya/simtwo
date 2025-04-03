// Handle AI Managed Preferences
document.getElementById("simtwo-ai-managed").addEventListener("change", (event) => {
  const aiManaged = event.target.checked;
  fetch("/api/set_preferences", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ ai_managed_preferences: aiManaged })
  })
  .then(response => response.json())
  .then(data => console.log(data));
});

// Handle Auto Trade Toggle
document.getElementById("auto-trade").addEventListener("change", (event) => {
  const autoTrade = event.target.checked;
  fetch("/api/set_preferences", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ auto_trade_enabled: autoTrade })
  })
  .then(response => response.json())
  .then(data => console.log(data));
});

// Emergency Stop Button
document.getElementById("emergency-stop-btn").addEventListener("click", () => {
  fetch("/api/emergency_stop", {
    method: "POST"
  })
  .then(response => response.json())
  .then(data => alert(data.status));
});

// Run Simulation Button