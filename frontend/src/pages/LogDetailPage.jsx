import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { Badge } from '../components/Badge'
import { Button } from '../components/Button'
import { useAuth } from '../hooks/useAuth'
import { logsAPI } from '../api/client'
import { ArrowLeft } from 'lucide-react'

export const LogDetailPage = () => {
  const { id } = useParams()
  const { token } = useAuth()
  const navigate = useNavigate()
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const response = await logsAPI.getDetectionDetail(id, token)
        setDetail(response.data)
      } catch (err) {
        console.error('Failed to load detail:', err)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchDetail()
    }
  }, [token, id])

  const getSeverityColor = (severity) => {
    const colors = {
      LOW: 'slate',
      MEDIUM: 'yellow',
      HIGH: 'red',
      CRITICAL: 'red',
    }
    return colors[severity] || 'slate'
  }

  const getDecisionColor = (decision) => {
    return decision === 'ALLOW' ? 'green' : 'red'
  }

  if (loading) {
    return (
      <Layout>
        <div className="text-center py-12 text-slate-600">Loading...</div>
      </Layout>
    )
  }

  if (!detail) {
    return (
      <Layout>
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-slate-600">Log not found.</p>
          </CardContent>
        </Card>
      </Layout>
    )
  }

  return (
    <Layout>
      <div>
        <button
          onClick={() => navigate('/logs')}
          className="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-6 font-medium"
        >
          <ArrowLeft size={18} />
          Back to Logs
        </button>

        <h1 className="text-3xl font-bold text-slate-900 mb-8">Detection Detail</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Prompt</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">
                    {detail.raw_prompt}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Classification</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-slate-600 mb-1">Category</p>
                  <p className="text-lg font-semibold text-slate-900">{detail.category_name}</p>
                </div>

                <div>
                  <p className="text-sm text-slate-600 mb-1">Confidence Score</p>
                  <p className="text-lg font-semibold text-slate-900">
                    {(detail.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-600 mb-1">Risk Score</p>
                  <div className="flex items-center gap-3">
                    <p className="text-2xl font-bold text-slate-900">
                      {detail.risk_score.toFixed(1)}
                    </p>
                    <Badge variant={getSeverityColor(detail.severity)}>
                      {detail.severity}
                    </Badge>
                  </div>
                </div>

                <div>
                  <p className="text-sm text-slate-600 mb-1">Firewall Decision</p>
                  <Badge variant={getDecisionColor(detail.decision)}>
                    {detail.decision}
                  </Badge>
                </div>

                <div>
                  <p className="text-sm text-slate-600 mb-1">Policy Rule</p>
                  <p className="text-sm font-mono bg-slate-50 p-2 rounded text-slate-700">
                    {detail.policy_rule_triggered}
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Analysis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-slate-600 mb-2">Classification Reason</p>
                  <p className="text-slate-700">{detail.classification_reason}</p>
                </div>

                <div>
                  <p className="text-sm text-slate-600 mb-2">Threat Explanation</p>
                  <p className="text-slate-700">{detail.threat_explanation}</p>
                </div>
              </CardContent>
            </Card>

            {detail.llm_response && (
              <Card>
                <CardHeader>
                  <CardTitle>LLM Response</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                    <p className="text-sm text-slate-700">{detail.llm_response}</p>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    Provider: <span className="font-semibold">{detail.llm_provider}</span>
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar Info */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4 text-sm">
                <div>
                  <p className="text-slate-600">Log ID</p>
                  <p className="font-mono text-xs text-slate-700 break-all">
                    {detail.prompt_log_id}
                  </p>
                </div>

                <div>
                  <p className="text-slate-600">Timestamp</p>
                  <p className="text-slate-700">
                    {new Date(detail.created_at).toLocaleString()}
                  </p>
                </div>

                <div>
                  <p className="text-slate-600">Decision</p>
                  <Badge variant={getDecisionColor(detail.decision)} className="mt-1">
                    {detail.decision}
                  </Badge>
                </div>

                <div>
                  <p className="text-slate-600">Severity</p>
                  <Badge variant={getSeverityColor(detail.severity)} className="mt-1">
                    {detail.severity}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  )
}