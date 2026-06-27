import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { Badge } from '../components/Badge'
import { useAuth } from '../hooks/useAuth'
import { logsAPI } from '../api/client'
import { ChevronRight } from 'lucide-react'

export const LogsPage = () => {
  const { token } = useAuth()
  const [activeTab, setActiveTab] = useState('threats')
  const [threats, setThreats] = useState([])
  const [prompts, setPrompts] = useState([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [severity, setSeverity] = useState(null)
  const [loading, setLoading] = useState(false)

  const pageSize = 20

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        if (activeTab === 'threats') {
          const response = await logsAPI.getThreatLogs(page, pageSize, severity, token)
          setThreats(response.data.items)
          setTotal(response.data.total)
        } else {
          const response = await logsAPI.getPromptLogs(page, pageSize, token)
          setPrompts(response.data.items)
          setTotal(response.data.total)
        }
      } catch (err) {
        console.error('Failed to load logs:', err)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchData()
    }
  }, [token, activeTab, page, severity])

  const getSeverityColor = (severity) => {
    const colors = {
      LOW: 'slate',
      MEDIUM: 'yellow',
      HIGH: 'red',
      CRITICAL: 'red',
    }
    return colors[severity] || 'slate'
  }

  const totalPages = Math.ceil(total / pageSize)

  return (
    <Layout>
      <div>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Attack Logs</h1>
        <p className="text-slate-600 mb-8">Review threat detection and firewall decision history.</p>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-slate-200">
          <button
            onClick={() => { setActiveTab('threats'); setPage(1) }}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === 'threats'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Threat Logs
          </button>
          <button
            onClick={() => { setActiveTab('prompts'); setPage(1) }}
            className={`px-4 py-2 font-medium text-sm transition-colors ${
              activeTab === 'prompts'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            All Prompts
          </button>
        </div>

        {/* Threat Logs Tab */}
        {activeTab === 'threats' && (
          <>
            <div className="mb-4">
              <select
                value={severity || ''}
                onChange={(e) => { setSeverity(e.target.value || null); setPage(1) }}
                className="px-4 py-2 border border-slate-200 rounded-lg text-slate-900"
              >
                <option value="">All Severities</option>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>

            {loading ? (
              <div className="text-center py-12 text-slate-600">Loading...</div>
            ) : threats.length > 0 ? (
              <>
                <div className="space-y-3 mb-6">
                  {threats.map((log) => (
                    <Link
                      key={log.id}
                      to={`/logs/${log.prompt_log_id}`}
                      className="block"
                    >
                      <Card className="hover:border-blue-300 cursor-pointer transition-colors">
                        <CardContent>
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <Badge variant={getSeverityColor(log.severity)}>
                                  {log.severity}
                                </Badge>
                                <span className="text-sm text-slate-600">
                                  {log.category_name}
                                </span>
                                {log.blocked && (
                                  <Badge variant="red">Blocked</Badge>
                                )}
                              </div>
                              <p className="text-sm text-slate-600">
                                Risk Score: <span className="font-semibold text-slate-900">{log.risk_score.toFixed(1)}</span>
                              </p>
                              <p className="text-xs text-slate-500 mt-1">
                                {new Date(log.created_at).toLocaleString()}
                              </p>
                            </div>
                            <ChevronRight className="text-slate-400" size={20} />
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>

                {/* Pagination */}
                <div className="flex justify-between items-center">
                  <p className="text-sm text-slate-600">
                    Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, total)} of {total}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="px-3 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>
                    <span className="px-3 py-2 text-slate-600">
                      Page {page} of {totalPages}
                    </span>
                    <button
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                      className="px-3 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-slate-600">No threat logs found.</p>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Prompts Tab */}
        {activeTab === 'prompts' && (
          <>
            {loading ? (
              <div className="text-center py-12 text-slate-600">Loading...</div>
            ) : prompts.length > 0 ? (
              <>
                <div className="space-y-3 mb-6">
                  {prompts.map((log) => (
                    <Card key={log.id} className="hover:border-blue-300 cursor-pointer transition-colors">
                      <CardContent>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm text-slate-700 line-clamp-2 mb-2">
                              {log.raw_prompt}
                            </p>
                            <div className="flex items-center gap-3 text-xs text-slate-500">
                              <span>ID: {log.id.substring(0, 8)}...</span>
                              <span>{new Date(log.created_at).toLocaleString()}</span>
                            </div>
                          </div>
                          <Badge variant="slate">{log.status}</Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Pagination */}
                <div className="flex justify-between items-center">
                  <p className="text-sm text-slate-600">
                    Showing {(page - 1) * pageSize + 1} - {Math.min(page * pageSize, total)} of {total}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(p => Math.max(1, p - 1))}
                      disabled={page === 1}
                      className="px-3 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>
                    <span className="px-3 py-2 text-slate-600">
                      Page {page} of {totalPages}
                    </span>
                    <button
                      onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                      className="px-3 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-slate-600">No prompts found.</p>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}