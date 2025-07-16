async function fetchLogs() {
  const res = await fetch("/api/logs/");
  const data = await res.json();
  // TODO: render logs in history page
}
window.onload = fetchLogs;

// Chart.js dashboard logic
if (document.getElementById("calorieChart")) {
  const calorieData = {
    daily: window.calorieDailyData,
    weekly: window.calorieWeeklyData,
    monthly: window.calorieMonthlyData,
  };
  const calorieLabels = {
    daily: window.calorieDailyLabels,
    weekly: window.calorieWeeklyLabels,
    monthly: window.calorieMonthlyLabels,
  };
  let currentView = "daily";
  const ctx = document.getElementById("calorieChart").getContext("2d");
  let chart = new Chart(ctx, {
    type: "line",
    data: {
      labels: calorieLabels.daily,
      datasets: [
        {
          label: "Calories",
          data: calorieData.daily,
          borderColor: "#059669",
          backgroundColor: "rgba(16,185,129,0.1)",
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
  document.getElementById("daily-btn").onclick = function () {
    chart.data.labels = calorieLabels.daily;
    chart.data.datasets[0].data = calorieData.daily;
    chart.update();
  };
  document.getElementById("weekly-btn").onclick = function () {
    chart.data.labels = calorieLabels.weekly;
    chart.data.datasets[0].data = calorieData.weekly;
    chart.update();
  };
  document.getElementById("monthly-btn").onclick = function () {
    chart.data.labels = calorieLabels.monthly;
    chart.data.datasets[0].data = calorieData.monthly;
    chart.update();
  };
}
