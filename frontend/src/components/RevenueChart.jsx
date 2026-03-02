/*
  RevenueChart.jsx
  line chart for monthly revenue trend with date range filter.
  uses recharts for the chart.
*/

import { useState, useMemo } from 'react'
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Area, AreaChart
} from 'recharts'

function formatCurrency(val) {
    return "$" + Number(val).toLocaleString("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    })
}

function RevenueChart({ data }) {
    const [fromDate, setFromDate] = useState("")
    const [toDate, setToDate] = useState("")

    // filter data based on date range
    const filteredData = useMemo(() => {
        let result = data
        if (fromDate) result = result.filter(d => d.month >= fromDate)
        if (toDate) result = result.filter(d => d.month <= toDate)
        return result
    }, [data, fromDate, toDate])

    return (
        <>
            <div className="card-header">
                <span className="card-title">📈 Monthly Revenue Trend</span>
                <div className="filters">
                    <label>From</label>
                    <input
                        type="month"
                        className="filter-input"
                        value={fromDate}
                        onChange={e => setFromDate(e.target.value)}
                    />
                    <label>To</label>
                    <input
                        type="month"
                        className="filter-input"
                        value={toDate}
                        onChange={e => setToDate(e.target.value)}
                    />
                </div>
            </div>
            <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                    <XAxis
                        dataKey="month"
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
                        formatter={(value) => [formatCurrency(value), "Revenue"]}
                        contentStyle={{
                            background: '#161b22',
                            border: '1px solid #30363d',
                            borderRadius: 6,
                            fontSize: 12,
                            color: '#e1e4e8'
                        }}
                    />
                    <Area
                        type="monotone"
                        dataKey="revenue"
                        stroke="#58a6ff"
                        fill="rgba(88, 166, 255, 0.1)"
                        strokeWidth={2}
                        dot={{ r: 2, fill: '#58a6ff' }}
                        activeDot={{ r: 4 }}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </>
    )
}

export default RevenueChart
