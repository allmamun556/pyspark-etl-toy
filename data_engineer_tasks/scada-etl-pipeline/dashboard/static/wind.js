function renderKpis(summary) {
  const lastRun = summary.last_run || {};
  const statusClass = lastRun.status === "success" ? "status-success" : lastRun.status === "failed" ? "status-failed" : "";
  const cards = [
    ["Turbines", summary.total_turbines ?? "-"],
    ["Readings", summary.total_readings ?? "-"],
    ["Fleet avg power (kW)", fmtNum(summary.avg_power_kw)],
    ["Fleet avg wind (m/s)", fmtNum(summary.avg_wind_speed_ms, 2)],
    ["Anomalies", summary.total_anomalies ?? "-"],
    ["Rejects", summary.total_rejects ?? "-"],
    ["Last run status", lastRun.status ?? "no runs yet", statusClass],
    ["Last run duration (s)", fmtNum(lastRun.duration_seconds, 2)],
  ];
  document.getElementById("kpi-row").innerHTML = cards
    .map(
      ([label, value, cls]) => `
      <div class="kpi-card">
        <div class="label">${label}</div>
        <div class="value ${cls || ""}">${value}</div>
      </div>`
    )
    .join("");
}

let fleetChart, timeseriesChart, powerCurveChart, runsChart;

function renderFleetChart(stats) {
  const ctx = document.getElementById("fleet-chart");
  const labels = stats.map((s) => s.turbine_id);
  const avgPower = stats.map((s) => s.avg_power_kw);
  const anomalyCounts = stats.map((s) => s.anomaly_count);

  if (fleetChart) {
    fleetChart.data.labels = labels;
    fleetChart.data.datasets[0].data = avgPower;
    fleetChart.data.datasets[1].data = anomalyCounts;
    fleetChart.update();
    return;
  }

  fleetChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Avg power (kW)", data: avgPower, backgroundColor: "#2563eb", yAxisID: "y" },
        { label: "Anomalies", data: anomalyCounts, backgroundColor: "#dc2626", yAxisID: "y1", type: "line", borderColor: "#dc2626", tension: 0.3 },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { position: "left", title: { display: true, text: "kW" } },
        y1: { position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "anomaly count" }, ticks: { precision: 0 } },
      },
    },
  });
}

async function renderTimeseries(turbineId) {
  const data = await getJSON(`/api/turbines/${turbineId}/timeseries?limit=200`);
  const labels = data.map((r) => new Date(r.ts).toLocaleTimeString());
  const wind = data.map((r) => r.wind_speed_ms);
  const power = data.map((r) => r.power_kw);

  const ctx = document.getElementById("timeseries-chart");
  if (timeseriesChart) {
    timeseriesChart.data.labels = labels;
    timeseriesChart.data.datasets[0].data = wind;
    timeseriesChart.data.datasets[1].data = power;
    timeseriesChart.update();
    return;
  }

  timeseriesChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Wind speed (m/s)", data: wind, borderColor: "#5b9dff", yAxisID: "y", tension: 0.25, pointRadius: 0 },
        { label: "Power (kW)", data: power, borderColor: "#f59e0b", yAxisID: "y1", tension: 0.25, pointRadius: 0 },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { position: "left", title: { display: true, text: "m/s" } },
        y1: { position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "kW" } },
      },
    },
  });
}

async function populateTurbineSelect() {
  const select = document.getElementById("turbine-select");
  if (select.options.length > 0) return select.value;
  const stats = await getJSON("/api/turbines/stats");
  select.innerHTML = stats.map((s) => `<option value="${s.turbine_id}">${s.turbine_id}</option>`).join("");
  select.addEventListener("change", () => renderTimeseries(select.value));
  return select.value;
}

async function refresh() {
  try {
    const [summary, latest, stats, runs, anomalies, rejects] = await Promise.all([
      getJSON("/api/summary"),
      getJSON("/api/turbines/latest"),
      getJSON("/api/turbines/stats"),
      getJSON("/api/audit/runs?limit=10&task_id=scada_etl_pipeline"),
      getJSON("/api/anomalies?limit=20"),
      getJSON("/api/rejects?limit=20"),
    ]);

    renderKpis(summary);
    renderFleetChart(stats);
    await refreshExternalPanel();

    const selectedTurbine = await populateTurbineSelect();
    if (selectedTurbine) await renderTimeseries(selectedTurbine);

    powerCurveChart = renderScatterChart(
      powerCurveChart,
      "power-curve-chart",
      latest.map((r) => ({
        x: Number(r.wind_speed_ms),
        y: Number(r.power_kw),
        label: r.turbine_id,
        anomalous: r.is_anomalous,
      })),
      { xLabel: "Wind speed (m/s)", yLabel: "Power (kW)" }
    );

    runsChart = renderRunsHealthChart(runsChart, "runs-chart", runs);

    renderDqEventsTable(
      "dq-events-table",
      anomalies,
      rejects,
      "turbine_id",
      (r) => `wind=${fmtNum(r.wind_speed_ms, 2)} power=${fmtNum(r.power_kw)} rpm=${fmtNum(r.rotor_rpm, 2)} status=${r.status_code}`
    );

    document.getElementById("last-updated").textContent = `updated ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    document.getElementById("last-updated").textContent = `error: ${err.message}`;
    console.error(err);
  }
}

refresh();
setInterval(refresh, REFRESH_MS);
