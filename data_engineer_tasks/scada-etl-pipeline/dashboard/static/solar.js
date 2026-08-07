function renderSolarKpis(summary) {
  const lastRun = summary.last_run || {};
  const statusClass = lastRun.status === "success" ? "status-success" : lastRun.status === "failed" ? "status-failed" : "";
  const cards = [
    ["Plants", summary.total_plants ?? "-"],
    ["Readings", summary.total_readings ?? "-"],
    ["Fleet avg DC power (kW)", fmtNum(summary.avg_dc_power_kw)],
    ["Fleet avg AC power (kW)", fmtNum(summary.avg_ac_power_kw)],
    ["Fleet avg irradiance (W/m²)", fmtNum(summary.avg_irradiance_w_m2, 1)],
    ["Anomalies", summary.total_anomalies ?? "-"],
    ["Rejects", summary.total_rejects ?? "-"],
    ["Last run status", lastRun.status ?? "no runs yet", statusClass],
    ["Last run duration (s)", fmtNum(lastRun.duration_seconds, 2)],
  ];
  document.getElementById("solar-kpi-row").innerHTML = cards
    .map(
      ([label, value, cls]) => `
      <div class="kpi-card">
        <div class="label">${label}</div>
        <div class="value ${cls || ""}">${value}</div>
      </div>`
    )
    .join("");
}

let solarFleetChart, solarTimeseriesChart, solarPowerCurveChart, solarRunsChart;

function renderSolarFleetChart(stats) {
  const ctx = document.getElementById("solar-fleet-chart");
  const labels = stats.map((s) => s.plant_id);
  const avgDcPower = stats.map((s) => s.avg_dc_power_kw);
  const anomalyCounts = stats.map((s) => s.anomaly_count);

  if (solarFleetChart) {
    solarFleetChart.data.labels = labels;
    solarFleetChart.data.datasets[0].data = avgDcPower;
    solarFleetChart.data.datasets[1].data = anomalyCounts;
    solarFleetChart.update();
    return;
  }

  solarFleetChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        { label: "Avg DC power (kW)", data: avgDcPower, backgroundColor: "#e0a458", yAxisID: "y" },
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

async function renderSolarTimeseries(plantId) {
  const data = await getJSON(`/api/solar/plants/${plantId}/timeseries?limit=200`);
  const labels = data.map((r) => new Date(r.ts).toLocaleTimeString());
  const irradiance = data.map((r) => r.irradiance_w_m2);
  const dcPower = data.map((r) => r.dc_power_kw);

  const ctx = document.getElementById("solar-timeseries-chart");
  if (solarTimeseriesChart) {
    solarTimeseriesChart.data.labels = labels;
    solarTimeseriesChart.data.datasets[0].data = irradiance;
    solarTimeseriesChart.data.datasets[1].data = dcPower;
    solarTimeseriesChart.update();
    return;
  }

  solarTimeseriesChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "Irradiance (W/m²)", data: irradiance, borderColor: "#e0a458", yAxisID: "y", tension: 0.25, pointRadius: 0 },
        { label: "DC power (kW)", data: dcPower, borderColor: "#2563eb", yAxisID: "y1", tension: 0.25, pointRadius: 0 },
      ],
    },
    options: {
      responsive: true,
      interaction: { mode: "index", intersect: false },
      scales: {
        y: { position: "left", title: { display: true, text: "W/m²" } },
        y1: { position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "kW" } },
      },
    },
  });
}

async function populatePlantSelect() {
  const select = document.getElementById("plant-select");
  if (select.options.length > 0) return select.value;
  const stats = await getJSON("/api/solar/plants/stats");
  select.innerHTML = stats.map((s) => `<option value="${s.plant_id}">${s.plant_id}</option>`).join("");
  select.addEventListener("change", () => renderSolarTimeseries(select.value));
  return select.value;
}

async function refresh() {
  try {
    const [solarSummary, solarLatest, solarStats, solarRuns, solarAnomalies, solarRejects] = await Promise.all([
      getJSON("/api/solar/summary"),
      getJSON("/api/solar/plants/latest"),
      getJSON("/api/solar/plants/stats"),
      getJSON("/api/audit/runs?limit=10&task_id=solar_etl_pipeline"),
      getJSON("/api/solar/anomalies?limit=20"),
      getJSON("/api/solar/rejects?limit=20"),
    ]);

    renderSolarKpis(solarSummary);
    renderSolarFleetChart(solarStats);
    await refreshExternalPanel();

    const selectedPlant = await populatePlantSelect();
    if (selectedPlant) await renderSolarTimeseries(selectedPlant);

    solarPowerCurveChart = renderScatterChart(
      solarPowerCurveChart,
      "solar-power-curve-chart",
      solarLatest.map((r) => ({
        x: Number(r.irradiance_w_m2),
        y: Number(r.dc_power_kw),
        label: r.plant_id,
        anomalous: r.is_anomalous,
      })),
      { xLabel: "Irradiance (W/m²)", yLabel: "DC power (kW)" }
    );

    solarRunsChart = renderRunsHealthChart(solarRunsChart, "solar-runs-chart", solarRuns);

    renderDqEventsTable(
      "solar-dq-events-table",
      solarAnomalies,
      solarRejects,
      "plant_id",
      (r) => `irradiance=${fmtNum(r.irradiance_w_m2, 1)} dc=${fmtNum(r.dc_power_kw)} ac=${fmtNum(r.ac_power_kw)} status=${r.status_code}`
    );

    document.getElementById("last-updated").textContent = `updated ${new Date().toLocaleTimeString()}`;
  } catch (err) {
    document.getElementById("last-updated").textContent = `error: ${err.message}`;
    console.error(err);
  }
}

refresh();
setInterval(refresh, REFRESH_MS);
