// Shared across index.html (wind) and solar.html - loaded before the
// page-specific script. Kept as plain globals (no bundler, no build step)
// since that's the whole point of this dashboard being vanilla JS.
const REFRESH_MS = 15000;

const fmtNum = (v, digits = 1) => (v === null || v === undefined ? "-" : Number(v).toFixed(digits));
const fmtTime = (v) => (v ? new Date(v).toLocaleString() : "-");

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

function renderTable(tableId, rows, rowFn, emptyText) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  if (!rows.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="10">${emptyText}</td></tr>`;
    return;
  }
  tbody.innerHTML = rows.map(rowFn).join("");
}

// Relevant to both dashboards - it's what anchors both the wind and solar
// simulators to reality (see README §7), so both pages show it.
async function refreshExternalPanel() {
  const external = await getJSON("/api/external");
  const weather = external.weather || {};
  const buoy = external.buoy || {};
  const cards = [
    ["Weather source", "Open-Meteo (HTTP API)"],
    ["Weather wind speed (m/s)", fmtNum(weather.wind_speed_ms, 2)],
    ["Weather temp (°C)", fmtNum(weather.temperature_c, 1)],
    ["Weather irradiance (W/m²)", fmtNum(weather.shortwave_radiation_w_m2, 1)],
    ["Weather updated", fmtTime(weather.ts)],
    ["Buoy source", `NOAA NDBC ${buoy.station_id || ""} (IoT)`],
    ["Buoy wind speed (m/s)", fmtNum(buoy.wind_speed_ms, 2)],
    ["Buoy wave height (m)", fmtNum(buoy.wave_height_m, 2)],
    ["Buoy updated", fmtTime(buoy.ts)],
  ];
  document.getElementById("external-kpi-row").innerHTML = cards
    .map(
      ([label, value]) => `
      <div class="kpi-card">
        <div class="label">${label}</div>
        <div class="value">${value}</div>
      </div>`
    )
    .join("");

  renderTable(
    "external-runs-table",
    external.recent_runs || [],
    (r) => `
      <tr>
        <td>${r.source}</td><td>${r.status}</td><td>${r.rows_fetched}</td>
        <td>${r.rows_loaded}</td><td>${r.rows_rejected}</td><td>${fmtNum(r.duration_seconds, 2)}</td>
        <td>${fmtTime(r.finished_at)}</td>
      </tr>`,
    "No external source runs yet"
  );
}
