const els = {
  modelStatus: document.querySelector("#modelStatus"),
  statusPanel: document.querySelector("#statusPanel"),
  statusText: document.querySelector("#statusText"),
  riskScore: document.querySelector("#riskScore"),
  threatText: document.querySelector("#threatText"),
  topReason: document.querySelector("#topReason"),
  deviceId: document.querySelector("#deviceId"),
  apCount: document.querySelector("#apCount"),
  unknownCount: document.querySelector("#unknownCount"),
  duplicateCount: document.querySelector("#duplicateCount"),
  openCount: document.querySelector("#openCount"),
  baselineCount: document.querySelector("#baselineCount"),
  reasonsList: document.querySelector("#reasonsList"),
  scanTime: document.querySelector("#scanTime"),
  networkRows: document.querySelector("#networkRows"),
  seedBtn: document.querySelector("#seedBtn"),
  learnBtn: document.querySelector("#learnBtn"),
  normalBtn: document.querySelector("#normalBtn"),
  attackBtn: document.querySelector("#attackBtn"),
};

async function postJson(path) {
  const response = await fetch(path, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function getStatus() {
  const response = await fetch("/api/status");
  if (!response.ok) {
    throw new Error(`Status failed: ${response.status}`);
  }
  return response.json();
}

function fmtTime(timestampMs) {
  if (!timestampMs) return "-";
  return new Date(timestampMs).toLocaleTimeString();
}

function statusClass(status) {
  if (status === "ALERT") return "alert";
  if (status === "WATCH") return "watch";
  if (status === "SAFE") return "safe";
  return "ready";
}

function numberValue(value) {
  return Number.isFinite(Number(value)) ? Math.round(Number(value)) : 0;
}

function render(data) {
  const features = data.features || {};
  const networks = data.networks || [];
  const reasons = data.reasons || [];
  const state = statusClass(data.status);

  els.statusPanel.dataset.state = state;
  els.modelStatus.textContent = `Model: ${data.model_status || "unknown"}`;
  els.statusText.textContent = data.status || "READY";
  els.riskScore.textContent = numberValue(data.risk_score);
  els.threatText.textContent = data.threat || "Waiting for scan";
  els.topReason.textContent = data.top_reason || reasons[0] || "No scan received yet.";
  els.deviceId.textContent = data.device_id || "No device";
  els.apCount.textContent = numberValue(features.ap_count ?? networks.length);
  els.unknownCount.textContent = numberValue(features.unknown_bssid_count);
  els.duplicateCount.textContent = numberValue(features.duplicate_ssid_count);
  els.openCount.textContent = numberValue(features.open_network_count);
  els.baselineCount.textContent = `${numberValue(data.baseline_count)} baseline APs`;
  els.scanTime.textContent = fmtTime(data.timestamp_ms);

  els.reasonsList.innerHTML = "";
  const reasonItems = reasons.length ? reasons : ["No detection reasons yet."];
  reasonItems.forEach((reason) => {
    const item = document.createElement("li");
    item.textContent = reason;
    els.reasonsList.appendChild(item);
  });

  els.networkRows.innerHTML = "";
  networks.forEach((net) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${escapeHtml(net.ssid || "")}</td>
      <td><code>${escapeHtml(net.bssid || "")}</code></td>
      <td>${numberValue(net.rssi)}</td>
      <td>${numberValue(net.channel)}</td>
      <td>${escapeHtml(net.encryption || "UNKNOWN")}</td>
    `;
    els.networkRows.appendChild(row);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function refresh() {
  try {
    render(await getStatus());
  } catch (error) {
    els.modelStatus.textContent = error.message;
  }
}

els.seedBtn.addEventListener("click", async () => {
  await postJson("/api/demo/seed");
  await refresh();
});

els.learnBtn.addEventListener("click", async () => {
  await postJson("/api/baseline/learn");
  await refresh();
});

els.normalBtn.addEventListener("click", async () => {
  render(await postJson("/api/demo/normal"));
});

els.attackBtn.addEventListener("click", async () => {
  render(await postJson("/api/demo/attack"));
});

refresh();
setInterval(refresh, 2500);
