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

// Wind and solar fleets both want a "power curve" scatter (x = the driving
// physical input, y = power output) built from the same /latest endpoint
// each page already fetches - shared here so the chart logic exists once.
// `existing` is the Chart instance from the previous call (or null on
// first render); returns the instance to keep for next time, Chart.js-style.
function renderScatterChart(existing, canvasId, points, opts) {
  const normal = points.filter((p) => !p.anomalous);
  const anomalous = points.filter((p) => p.anomalous);

  if (existing) {
    existing.data.datasets[0].data = normal;
    existing.data.datasets[1].data = anomalous;
    existing.update();
    return existing;
  }

  const ctx = document.getElementById(canvasId);
  return new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        { label: "Normal", data: normal, backgroundColor: "#2563eb" },
        { label: "Anomalous", data: anomalous, backgroundColor: "#dc2626" },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: { callbacks: { label: (item) => `${item.raw.label}: (${item.raw.x}, ${item.raw.y})` } },
      },
      scales: {
        x: { title: { display: true, text: opts.xLabel } },
        y: { title: { display: true, text: opts.yLabel } },
      },
    },
  });
}

// Same idea for the "recent pipeline runs" chart - rows loaded/rejected as
// bars, duration as a line on a secondary axis. Both fleets' /api/audit/runs
// responses have identical shape, so this is shared as-is.
function renderRunsHealthChart(existing, canvasId, runs) {
  const ordered = [...runs].reverse(); // oldest -> newest, left to right
  const labels = ordered.map((r) => fmtTime(r.finished_at));
  const loaded = ordered.map((r) => r.rows_loaded);
  const rejected = ordered.map((r) => r.rows_rejected);
  const duration = ordered.map((r) => Number(r.duration_seconds));

  if (existing) {
    existing.data.labels = labels;
    existing.data.datasets[0].data = loaded;
    existing.data.datasets[1].data = rejected;
    existing.data.datasets[2].data = duration;
    existing.update();
    return existing;
  }

  const ctx = document.getElementById(canvasId);
  return new Chart(ctx, {
    data: {
      labels,
      datasets: [
        { type: "bar", label: "Rows loaded", data: loaded, backgroundColor: "#16a34a", yAxisID: "y" },
        { type: "bar", label: "Rows rejected", data: rejected, backgroundColor: "#dc2626", yAxisID: "y" },
        { type: "line", label: "Duration (s)", data: duration, borderColor: "#f59e0b", yAxisID: "y1", tension: 0.3, pointRadius: 2 },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { position: "left", title: { display: true, text: "rows" }, ticks: { precision: 0 } },
        y1: { position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "seconds" } },
      },
    },
  });
}

// Anomalies (from readings) and rejects (from validation) have different
// shapes, so each fleet passes its own `anomalyDetailFn` to format the
// anomaly side into the same "Detail" column rejects already use
// (reject_reason is already a plain string).
function renderDqEventsTable(tableId, anomalies, rejects, idField, anomalyDetailFn) {
  const events = [
    ...anomalies.map((r) => ({ id: r[idField], ts: r.ts, type: "anomaly", detail: anomalyDetailFn(r) })),
    ...rejects.map((r) => ({ id: r[idField], ts: r.rejected_at, type: "reject", detail: r.reject_reason })),
  ].sort((a, b) => new Date(b.ts) - new Date(a.ts));

  renderTable(
    tableId,
    events,
    (e) => `
      <tr class="${e.type === "anomaly" ? "anomalous" : ""}">
        <td>${e.id}</td><td>${fmtTime(e.ts)}</td><td>${e.type}</td><td>${e.detail}</td>
      </tr>`,
    "No data quality events"
  );
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
