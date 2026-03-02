/*
  CategoryChart.jsx
  bar chart showing revenue by product category.
*/

import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Cell
} from 'recharts'

// colors for the bars
const COLORS = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#bc8cff", "#79c0ff"]

function formatCurrency(val) {
    return "$" + Number(val).toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    })
}

function CategoryChart({ data }) {
    return (
        <>
            <div className="card-header">
                <span className="card-title">📦 Category Breakdown</span>
            </div>
            <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis
                        dataKey="category"
                        tick={{ fill: '#8b949e', fontSize: 11 }}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fill: '#8b949e', fontSize: 11 }}
                        tickFormatter={formatCurrency}
                        tickLine={false}
                        width={70}
                    />
                    <Tooltip
                        formatter={(value, name, props) => {
                            const item = props.payload
                            return [
                                formatCurrency(value),
                                `Revenue (Avg: ${formatCurrency(item.avg_order_value)}, Orders: ${item.num_orders})`
                            ]
                        }}
                        contentStyle={{
                            background: '#161b22',
                            border: '1px solid #30363d',
                            borderRadius: 6,
                            fontSize: 12,
                            color: '#e1e4e8'
                        }}
                    />
                    <Bar dataKey="total_revenue" radius={[4, 4, 0, 0]}>
                        {data.map((entry, i) => (
                            <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </>
    )
}

export default CategoryChart
