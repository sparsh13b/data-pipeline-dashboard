/*
  app.js
  fetches data from the backend api and renders the dashboard.
  uses chart.js for charts, vanilla js for everything else.
*/

const API_BASE = "http://localhost:8000";

// ---- utility helpers ----

function formatCurrency(val) {
    // format number as $1,234.56
    return "$" + Number(val).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function showLoading(id) {
    document.getElementById(id + "-loading").style.display = "flex";
    document.getElementById(id + "-error").style.display = "none";
}

function hideLoading(id) {
    document.getElementById(id + "-loading").style.display = "none";
}

function showError(id) {
    document.getElementById(id + "-loading").style.display = "none";
    document.getElementById(id + "-error").style.display = "block";
}

async function fetchData(endpoint) {
    const resp = await fetch(API_BASE + endpoint);
    if (!resp.ok) throw new Error(`api error: ${resp.status}`);
    return await resp.json();
}


// ---- revenue chart ----

let revenueChart = null;
let allRevenueData = [];

async function loadRevenue() {
    showLoading("revenue");
    try {
        allRevenueData = await fetchData("/api/revenue");
        renderRevenueChart(allRevenueData);
        setupDateFilters(allRevenueData);
        hideLoading("revenue");
    } catch (err) {
        console.error("revenue error:", err);
        showError("revenue");
    }
}

function renderRevenueChart(data) {
    const ctx = document.getElementById("revenue-chart");

    // destroy old chart if exists
    if (revenueChart) revenueChart.destroy();

    revenueChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: data.map(d => d.month),
            datasets: [{
                label: "Revenue",
                data: data.map(d => d.revenue),
                borderColor: "#58a6ff",
                backgroundColor: "rgba(88, 166, 255, 0.1)",
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return "Revenue: " + formatCurrency(ctx.parsed.y);
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#8b949e", maxTicksLimit: 12 },
                    grid: { color: "#21262d" }
                },
                y: {
                    ticks: {
                        color: "#8b949e",
                        callback: val => formatCurrency(val)
                    },
                    grid: { color: "#21262d" }
                }
            }
        }
    });
}

function setupDateFilters(data) {
    if (data.length === 0) return;

    const fromInput = document.getElementById("date-from");
    const toInput = document.getElementById("date-to");

    // set min/max based on data
    fromInput.min = data[0].month;
    fromInput.max = data[data.length - 1].month;
    toInput.min = data[0].month;
    toInput.max = data[data.length - 1].month;

    // filter handler
    function applyFilter() {
        const from = fromInput.value;
        const to = toInput.value;

        let filtered = allRevenueData;
        if (from) filtered = filtered.filter(d => d.month >= from);
        if (to) filtered = filtered.filter(d => d.month <= to);

        renderRevenueChart(filtered);
    }

    fromInput.addEventListener("change", applyFilter);
    toInput.addEventListener("change", applyFilter);
}


// ---- top customers table ----

let allCustomersData = [];
let sortCol = "total_spend";
let sortAsc = false; // default descending by spend

async function loadTopCustomers() {
    showLoading("customers");
    try {
        allCustomersData = await fetchData("/api/top-customers");
        renderCustomersTable(allCustomersData);
        hideLoading("customers");
    } catch (err) {
        console.error("customers error:", err);
        showError("customers");
    }
}

function renderCustomersTable(data) {
    const tbody = document.querySelector("#customers-table tbody");
    tbody.innerHTML = "";

    // sort the data
    const sorted = [...data].sort((a, b) => {
        let valA = a[sortCol];
        let valB = b[sortCol];

        // handle numeric vs string
        if (typeof valA === "number" && typeof valB === "number") {
            return sortAsc ? valA - valB : valB - valA;
        }

        valA = String(valA || "").toLowerCase();
        valB = String(valB || "").toLowerCase();
        if (valA < valB) return sortAsc ? -1 : 1;
        if (valA > valB) return sortAsc ? 1 : -1;
        return 0;
    });

    sorted.forEach(row => {
        const tr = document.createElement("tr");
        const churned = row.churned === true || row.churned === "True";

        tr.innerHTML = `
            <td>${row.name || "N/A"}</td>
            <td>${row.region || "Unknown"}</td>
            <td>${formatCurrency(row.total_spend)}</td>
            <td>
                <span class="badge ${churned ? 'badge-churned' : 'badge-active'}">
                    ${churned ? 'Churned' : 'Active'}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });

    // update sort indicators
    document.querySelectorAll("#customers-table thead th").forEach(th => {
        th.classList.toggle("active", th.dataset.col === sortCol);
        const arrow = th.querySelector(".sort-arrow");
        if (th.dataset.col === sortCol) {
            arrow.textContent = sortAsc ? "▲" : "▼";
        } else {
            arrow.textContent = "▲";
        }
    });
}

// sort click handlers
document.querySelectorAll("#customers-table thead th").forEach(th => {
    th.addEventListener("click", () => {
        const col = th.dataset.col;
        if (sortCol === col) {
            sortAsc = !sortAsc;
        } else {
            sortCol = col;
            sortAsc = true;
        }
        // re-render with current (possibly filtered) data
        const searchTerm = document.getElementById("customer-search").value.toLowerCase();
        const filtered = filterCustomers(searchTerm);
        renderCustomersTable(filtered);
    });
});

// search box
document.getElementById("customer-search").addEventListener("input", function () {
    const term = this.value.toLowerCase();
    const filtered = filterCustomers(term);
    renderCustomersTable(filtered);
});

function filterCustomers(term) {
    if (!term) return allCustomersData;
    return allCustomersData.filter(row => {
        const name = (row.name || "").toLowerCase();
        const region = (row.region || "").toLowerCase();
        return name.includes(term) || region.includes(term);
    });
}


// ---- category chart ----

let categoryChart = null;

async function loadCategories() {
    showLoading("category");
    try {
        const data = await fetchData("/api/categories");
        renderCategoryChart(data);
        hideLoading("category");
    } catch (err) {
        console.error("category error:", err);
        showError("category");
    }
}

function renderCategoryChart(data) {
    const ctx = document.getElementById("category-chart");

    if (categoryChart) categoryChart.destroy();

    // nice color palette
    const colors = [
        "#58a6ff", "#3fb950", "#d29922", "#f85149",
        "#bc8cff", "#79c0ff", "#56d364", "#e3b341",
        "#ff7b72", "#d2a8ff"
    ];

    categoryChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.map(d => d.category),
            datasets: [{
                label: "Revenue",
                data: data.map(d => d.total_revenue),
                backgroundColor: data.map((_, i) => colors[i % colors.length]),
                borderRadius: 4,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const item = data[ctx.dataIndex];
                            return [
                                "Revenue: " + formatCurrency(item.total_revenue),
                                "Avg Order: " + formatCurrency(item.avg_order_value),
                                "Orders: " + item.num_orders,
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#8b949e" },
                    grid: { display: false }
                },
                y: {
                    ticks: {
                        color: "#8b949e",
                        callback: val => formatCurrency(val)
                    },
                    grid: { color: "#21262d" }
                }
            }
        }
    });
}


// ---- region summary cards ----

async function loadRegions() {
    showLoading("region");
    try {
        const data = await fetchData("/api/regions");
        renderRegionCards(data);
        hideLoading("region");
    } catch (err) {
        console.error("region error:", err);
        showError("region");
    }
}

function renderRegionCards(data) {
    const grid = document.getElementById("region-grid");
    grid.innerHTML = "";

    data.forEach(region => {
        const card = document.createElement("div");
        card.className = "region-card";
        card.innerHTML = `
            <h3>${region.region || "Unknown"}</h3>
            <div class="region-stat">
                <span>Customers</span>
                <span class="value">${region.num_customers}</span>
            </div>
            <div class="region-stat">
                <span>Orders</span>
                <span class="value">${region.num_orders}</span>
            </div>
            <div class="region-stat">
                <span>Revenue</span>
                <span class="value">${formatCurrency(region.total_revenue)}</span>
            </div>
            <div class="region-stat">
                <span>Avg/Customer</span>
                <span class="value">${formatCurrency(region.avg_revenue_per_customer)}</span>
            </div>
        `;
        grid.appendChild(card);
    });
}


// ---- kick everything off ----

document.addEventListener("DOMContentLoaded", () => {
    loadRevenue();
    loadTopCustomers();
    loadCategories();
    loadRegions();
});
