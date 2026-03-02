/*
  TopCustomers.jsx
  sortable table with search for top 10 customers.
*/

import { useState, useMemo } from 'react'

function formatCurrency(val) {
    return "$" + Number(val).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    })
}

function TopCustomers({ data }) {
    const [search, setSearch] = useState("")
    const [sortCol, setSortCol] = useState("total_spend")
    const [sortAsc, setSortAsc] = useState(false)

    // handle column header click
    function handleSort(col) {
        if (sortCol === col) {
            setSortAsc(!sortAsc)
        } else {
            setSortCol(col)
            setSortAsc(true)
        }
    }

    // filter + sort the data
    const displayData = useMemo(() => {
        let result = data

        // search filter
        if (search) {
            const term = search.toLowerCase()
            result = result.filter(row =>
                (row.name || "").toLowerCase().includes(term) ||
                (row.region || "").toLowerCase().includes(term)
            )
        }

        // sort
        result = [...result].sort((a, b) => {
            let valA = a[sortCol]
            let valB = b[sortCol]

            if (typeof valA === "number" && typeof valB === "number") {
                return sortAsc ? valA - valB : valB - valA
            }

            valA = String(valA || "").toLowerCase()
            valB = String(valB || "").toLowerCase()
            if (valA < valB) return sortAsc ? -1 : 1
            if (valA > valB) return sortAsc ? 1 : -1
            return 0
        })

        return result
    }, [data, search, sortCol, sortAsc])

    // helper for sort arrow
    function getArrow(col) {
        if (sortCol !== col) return "▲"
        return sortAsc ? "▲" : "▼"
    }

    return (
        <>
            <div className="card-header">
                <span className="card-title">🏆 Top Customers</span>
                <input
                    type="text"
                    className="search-box"
                    placeholder="Search by name or region..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
            </div>
            <div className="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            {[
                                { key: "name", label: "Name" },
                                { key: "region", label: "Region" },
                                { key: "total_spend", label: "Total Spend" },
                                { key: "churned", label: "Status" },
                            ].map(col => (
                                <th
                                    key={col.key}
                                    className={sortCol === col.key ? "active" : ""}
                                    onClick={() => handleSort(col.key)}
                                >
                                    {col.label}
                                    <span className="sort-arrow">{getArrow(col.key)}</span>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {displayData.map((row, i) => {
                            const churned = row.churned === true || row.churned === "True"
                            return (
                                <tr key={i}>
                                    <td>{row.name || "N/A"}</td>
                                    <td>{row.region || "Unknown"}</td>
                                    <td>{formatCurrency(row.total_spend)}</td>
                                    <td>
                                        <span className={`badge ${churned ? 'badge-churned' : 'badge-active'}`}>
                                            {churned ? "Churned" : "Active"}
                                        </span>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        </>
    )
}

export default TopCustomers
