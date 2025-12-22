//https://www.chartjs.org/docs/latest/samples/line/line.html for chart.js
//https://www.youtube.com/watch?v=herKZzGfEZY&t=354s for how to import sql to chart.js

document.addEventListener('DOMContentLoaded', () => {
  const sel = document.getElementById('eventSelect');
  const ctx = document.getElementById('swim_chart')?.getContext('2d');
  const noDataMsg = document.getElementById('noDataMsg');

  if (!ctx) return; // no canvas on page

  // 1) Create the chart with empty data
  const chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Race time (sec)',
        data: [],
        borderWidth: 2,
        tension: 0.25,
        pointRadius: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { reverse: true, title: { display: true, text: 'Seconds: ' } },
        x: { ticks: { autoSkip: true, maxTicksLimit: 10 } }
      }
    }
  });

  // 2) Loader: fetch JSON and update the chart
  async function load(eventName) {
    if (!eventName) return;
    const res = await fetch(`/progression?format=json&event=${encodeURIComponent(eventName)}`);
    if (!res.ok) { console.error('Fetch failed'); return; }
    const json = await res.json();
    console.log(json); // sanity check once

    chart.data.labels = json.labels || [];
    chart.data.datasets[0].data = json.values || [];
    chart.update();

    if (noDataMsg) noDataMsg.style.display = (chart.data.labels.length ? 'none' : 'block');
  }

  // 3) Initial load + dropdown change
  if (sel) {
    if (sel.value) load(sel.value);
    sel.addEventListener('change', () => load(sel.value));
  }
});
