/*
  App.jsx
  main dashboard layout - fetches data and renders the 4 sections.
  nothing fancy, just a clean layout.
*/

import { useState, useEffect } from 'react'
import RevenueChart from './components/RevenueChart'
import TopCustomers from './components/TopCustomers'
import CategoryChart from './components/CategoryChart'
import RegionSummary from './components/RegionSummary'

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

// helper to fetch from our api
async function fetchData(endpoint) {
    const res = await fetch(API_BASE + endpoint)
    if (!res.ok) throw new Error(`api returned ${res.status}`)
    return res.json()
}

function App() {
    // revenue state
    const [revenue, setRevenue] = useState([])
    const [revenueLoading, setRevenueLoading] = useState(true)
    const [revenueError, setRevenueError] = useState(null)

    // customers state
    const [customers, setCustomers] = useState([])
    const [customersLoading, setCustomersLoading] = useState(true)
    const [customersError, setCustomersError] = useState(null)

    // categories state
    const [categories, setCategories] = useState([])
    const [categoriesLoading, setCategoriesLoading] = useState(true)
    const [categoriesError, setCategoriesError] = useState(null)

    // regions state
    const [regions, setRegions] = useState([])
    const [regionsLoading, setRegionsLoading] = useState(true)
    const [regionsError, setRegionsError] = useState(null)

    // fetch all data on mount
    const loadRevenue = () => {
        setRevenueLoading(true)
        setRevenueError(null)
        fetchData("/api/revenue")
            .then(data => { setRevenue(data); setRevenueLoading(false) })
            .catch(err => { setRevenueError(err.message); setRevenueLoading(false) })
    }

    const loadCustomers = () => {
        setCustomersLoading(true)
        setCustomersError(null)
        fetchData("/api/top-customers")
            .then(data => { setCustomers(data); setCustomersLoading(false) })
            .catch(err => { setCustomersError(err.message); setCustomersLoading(false) })
    }

    const loadCategories = () => {
        setCategoriesLoading(true)
        setCategoriesError(null)
        fetchData("/api/categories")
            .then(data => { setCategories(data); setCategoriesLoading(false) })
            .catch(err => { setCategoriesError(err.message); setCategoriesLoading(false) })
    }

    const loadRegions = () => {
        setRegionsLoading(true)
        setRegionsError(null)
        fetchData("/api/regions")
            .then(data => { setRegions(data); setRegionsLoading(false) })
            .catch(err => { setRegionsError(err.message); setRegionsLoading(false) })
    }

    useEffect(() => {
        loadRevenue()
        loadCustomers()
        loadCategories()
        loadRegions()
    }, [])

    return (
        <>
            <header className="header">
                <h1>📊 Data Pipeline Dashboard</h1>
                <span className="subtitle">Business analytics from processed pipeline data</span>
            </header>

            <main className="dashboard">
                {/* revenue trend - full width */}
                <div className="card full-width">
                    {revenueLoading ? (
                        <div className="loading"><div className="spinner"></div> Loading revenue data...</div>
                    ) : revenueError ? (
                        <div className="error-msg">
                            <p>Failed to load revenue data</p>
                            <button className="retry-btn" onClick={loadRevenue}>Retry</button>
                        </div>
                    ) : (
                        <RevenueChart data={revenue} />
                    )}
                </div>

                {/* top customers - full width */}
                <div className="card full-width">
                    {customersLoading ? (
                        <div className="loading"><div className="spinner"></div> Loading customer data...</div>
                    ) : customersError ? (
                        <div className="error-msg">
                            <p>Failed to load customer data</p>
                            <button className="retry-btn" onClick={loadCustomers}>Retry</button>
                        </div>
                    ) : (
                        <TopCustomers data={customers} />
                    )}
                </div>

                {/* category breakdown */}
                <div className="card">
                    {categoriesLoading ? (
                        <div className="loading"><div className="spinner"></div> Loading...</div>
                    ) : categoriesError ? (
                        <div className="error-msg">
                            <p>Failed to load category data</p>
                            <button className="retry-btn" onClick={loadCategories}>Retry</button>
                        </div>
                    ) : (
                        <CategoryChart data={categories} />
                    )}
                </div>

                {/* region summary */}
                <div className="card">
                    {regionsLoading ? (
                        <div className="loading"><div className="spinner"></div> Loading...</div>
                    ) : regionsError ? (
                        <div className="error-msg">
                            <p>Failed to load region data</p>
                            <button className="retry-btn" onClick={loadRegions}>Retry</button>
                        </div>
                    ) : (
                        <RegionSummary data={regions} />
                    )}
                </div>
            </main>
        </>
    )
}

export default App
