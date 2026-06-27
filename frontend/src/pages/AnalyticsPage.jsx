import React, { useState, useEffect } from 'react'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { useAuth } from '../hooks/useAuth'
import { analyticsAPI } from '../api/client'
import { Badge } from '../components/Badge'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

export const AnalyticsPage = () => {
  const { token } = useAuth()
  const [overview, setOverview] = useState(null)
  const [categories, setCategories] = useState([])
  const [severity, setSeverity] = useState([])
  const [trends, setTrends] = useState([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const [overRes, catRes, sevRes, trendRes] = await Promise.all([
          analyticsAPI.getOverview(days, token),
          analyticsAPI.getCategories(days, token),
          analyticsAPI.getSeverity(days, token),
          analyticsAPI.getTrends(Math.min(days, 14), token),
        ])
        setOverview(overRes.data)
        setCategories(catRes.data)
        setSeverity(sevRes.data)
        setTrends(trendRes.data)
      } catch (err) {
        console.error('Failed to load analytics:', err)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchData()
    }
  }, [token, days])

  const CATEGORY_COLORS = [
    '#3b82f6', '#ef4444', '#8b5cf6', '#ec4899',
    '#f59e0b', '#10b981', '#06b6d4', '#6366f1',
  ]

  const SEVERITY_COLORS = {
    LOW: '#10b981',
    MEDIUM: '#f59e0b',
    HIGH: '#ef4444',
    CRITICAL: '#991b1b',
  }

  return (
    <Layout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Threat Analytics</h1>
            <p className="text-slate-600">Monitor security trends and threat patterns.</p>
          </div>
          <div>
            <select
              value={days}
              onChange={(e) => setDays(parseInt(e.target.value))}
              className="px-4 py-2 border border-slate-200 rounded-lg text-slate-900"
            >
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-600">Loading analytics...</div>
        ) : (
          <>
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-1">Total Requests</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {overview?.total_requests || 0}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-1">Allowed</p>
                  <p className="text-3xl font-bold text-green-600">
                    {overview?.total_allowed || 0}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-1">Blocked</p>
                  <p className="text-3xl font-bold text-red-600">
                    {overview?.total_blocked || 0}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-1">Block Rate</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {overview?.block_rate || 0}%
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Risk & Confidence */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <Card>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-1">Average Risk Score</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {overview?.avg_risk_score?.toFixed(1) || 0}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardContent>
                  <p className="text-sm text-slate-600 mb-1">Average Confidence</p>
                  <p className="text-3xl font-bold text-slate-900">
                    {(overview?.avg_confidence_score * 100)?.toFixed(1) || 0}%
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Trends Chart */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Request Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trends}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total_requests"
                      stroke="#3b82f6"
                      name="Total Requests"
                    />
                    <Line
                      type="monotone"
                      dataKey="total_allowed"
                      stroke="#10b981"
                      name="Allowed"
                    />
                    <Line
                      type="monotone"
                      dataKey="total_blocked"
                      stroke="#ef4444"
                      name="Blocked"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Category & Severity Charts */}
                        {/* Category & Severity Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Threat Categories</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={categories}
                        dataKey="count"
                        nameKey="category_name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {categories.map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Severity Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {severity.map((item) => (
                      <div
                        key={item.severity}
                        className="flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3">
                          <Badge
                            variant={
                              item.severity === 'CRITICAL'
                                ? 'red'
                                : item.severity === 'HIGH'
                                ? 'red'
                                : item.severity === 'MEDIUM'
                                ? 'yellow'
                                : 'slate'
                            }
                          >
                            {item.severity}
                          </Badge>
                        </div>
                        <span className="font-semibold text-slate-900">
                          {item.count}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </Layout>
  )
}
            