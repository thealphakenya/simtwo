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
  .then(data => {
    console.log(data);
    alert(`AI Managed Preferences updated: ${aiManaged ? 'Enabled' : 'Disabled'}`);
  })
  .catch(error => {
    console.error('Error:', error);
    alert("Failed to update AI Managed Preferences");
  });
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
  .then(data => {
    console.log(data);
    alert(`Auto Trade updated: ${autoTrade ? 'Enabled' : 'Disabled'}`);
  })
  .catch(error => {
    console.error('Error:', error);
    alert("Failed to update Auto Trade");
  });
});

// Emergency Stop Button
document.getElementById("emergency-stop-btn").addEventListener("click", () => {
  fetch("/api/emergency_stop", {
    method: "POST"
  })
  .then(response => response.json())
  .then(data => {
    alert(data.status);
  })
  .catch(error => {
    console.error('Error:', error);
    alert("Failed to activate Emergency Stop");
  });
});

// Run Simulation Button
document.getElementById("run-simulation-btn").addEventListener("click", () => {
  fetch("/api/run_simulation", {
    method: "POST"
  })
  .then(response => response.json())
  .then(data => {
    // Display the simulation results
    console.log(data);
    alert(`Simulation Results: \nP&L: ${data['P&L']} \nSharpe Ratio: ${data['Sharpe Ratio']} \nWin Rate: ${data['Win Rate']}% \nMax Drawdown: ${data['Max Drawdown']}%`);
  })
  .catch(error => {
    console.error('Error:', error);
    alert("Failed to run simulation");
  });
});
