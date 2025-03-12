// app.js

// API Base URL
const API_BASE = "http://127.0.0.1:5000";

// Elements
const totalIncomeElem = document.getElementById("total-income");
const totalExpensesElem = document.getElementById("total-expenses");
const remainingBudgetElem = document.getElementById("remaining-budget");
const expenseForm = document.getElementById("expense-form");
const incomeForm = document.getElementById("income-form");
const spendingTrendsChart = document.getElementById("spending-trends-chart").getContext("2d");

// Fetch Dashboard Data
async function fetchDashboardData() {
  const response = await fetch(`${API_BASE}/budget_status`);
  const data = await response.json();
  totalIncomeElem.textContent = data.total_income;
  totalExpensesElem.textContent = data.total_expenses;
  remainingBudgetElem.textContent = data.remaining_budget;
}

// Fetch Spending Trends
async function fetchSpendingTrends() {
  const response = await fetch(`${API_BASE}/spending_trends`);
  const data = await response.json();

  const labels = data.trends.map(trend => trend._id);
  const amounts = data.trends.map(trend => trend.total);

  new Chart(spendingTrendsChart, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data: amounts,
        backgroundColor: ["#f44336", "#ff9800", "#4caf50", "#2196f3"],
      }]
    }
  });
}

// Add Expense
expenseForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const category = document.getElementById("expense-category").value;
  const amount = parseFloat(document.getElementById("expense-amount").value);
  const date = document.getElementById("expense-date").value;
  const description = document.getElementById("expense-description").value;

  await fetch(`${API_BASE}/add_expense`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category, amount, date, description })
  });

  fetchDashboardData();
  fetchSpendingTrends();
});

// Add Income
incomeForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const source = document.getElementById("income-source").value;
  const amount = parseFloat(document.getElementById("income-amount").value);
  const date = document.getElementById("income-date").value;

  await fetch(`${API_BASE}/add_income`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, amount, date })
  });

  fetchDashboardData();
});

// Initialize Dashboard
fetchDashboardData();
fetchSpendingTrends();