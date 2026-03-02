/*
  RegionSummary.jsx
  card-based view of region KPIs.
*/

function formatCurrency(val) {
    return "$" + Number(val).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })
}

function RegionSummary({ data }) {
    return (
        <>
            <div className="card-header">
                <span className="card-title">🌍 Region Summary</span>
            </div>
            <div className="region-grid">
                {data.map((region, i) => (
                    <div className="region-card" key={i}>
                        <h3>{region.region || "Unknown"}</h3>
                        <div className="region-stat">
                            <span>Customers</span>
                            <span className="value">{region.num_customers}</span>
                        </div>
                        <div className="region-stat">
                            <span>Orders</span>
                            <span className="value">{region.num_orders}</span>
                        </div>
                        <div className="region-stat">
                            <span>Revenue</span>
                            <span className="value">{formatCurrency(region.total_revenue)}</span>
                        </div>
                        <div className="region-stat">
                            <span>Avg/Customer</span>
                            <span className="value">{formatCurrency(region.avg_revenue_per_customer)}</span>
                        </div>
                    </div>
                ))}
            </div>
        </>
    )
}

export default RegionSummary
