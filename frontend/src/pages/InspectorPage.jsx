import React, { useState } from 'react'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { Button } from '../components/Button'
import { Textarea } from '../components/Input'
import { Badge } from '../components/Badge'
import { useAuth } from '../hooks/useAuth'
import { firewallAPI } from '../api/client'

// Lightweight markdown -> HTML for rendering LLM answers (headers, bold, italic, lists, hr, paragraphs)
const formatMarkdown = (text) => {
  if (!text) return ''
  const escapeHtml = (s) => s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  const lines = escapeHtml(text).split('\n')
  let html = ''
  let inList = false

  const inline = (s) => s
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="bg-slate-100 px-1 rounded text-xs">$1</code>')

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (line === '') {
      if (inList) { html += '</ul>'; inList = false }
      continue
    }
    if (/^---+$/.test(line)) {
      if (inList) { html += '</ul>'; inList = false }
      html += '<hr class="my-3 border-slate-200" />'
      continue
    }
    const headerMatch = line.match(/^(#{1,6})\s+(.*)$/)
    if (headerMatch) {
      if (inList) { html += '</ul>'; inList = false }
      const level = headerMatch[1].length
      const sizeClass = level <= 2 ? 'text-lg font-bold mt-3 mb-1' : 'text-base font-semibold mt-2 mb-1'
      html += `<div class="${sizeClass}">${inline(headerMatch[2])}</div>`
      continue
    }
    const listMatch = line.match(/^[*-]\s+(.*)$/)
    if (listMatch) {
      if (!inList) { html += '<ul class="list-disc pl-5 space-y-1 my-1">'; inList = true }
      html += `<li>${inline(listMatch[1])}</li>`
      continue
    }
    if (inList) { html += '</ul>'; inList = false }
    html += `<p class="my-1">${inline(line)}</p>`
  }
  if (inList) html += '</ul>'
  return html
}

export const InspectorPage = () => {
  const { token } = useAuth()
  const [prompt, setPrompt] = useState('')
  const [provider, setProvider] = useState('gemini')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAnalyze = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt')
      return
    }

    setLoading(true)
    setError('')
    try {
      const response = await firewallAPI.analyze(prompt, provider, token)
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

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

  return (
    <Layout>
      <div>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Prompt Inspector</h1>
        <p className="text-slate-600 mb-8">Analyze a prompt in real-time to see how the firewall classifies it.</p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Enter Prompt</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  label="Prompt to analyze"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Paste your prompt here..."
                  rows={6}
                />

                <div className="mb-4">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    LLM Provider
                  </label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full px-4 py-2 border border-slate-200 rounded-lg text-slate-900"
                  >
                    <option value="gemini">Gemini</option>
                  </select>
                </div>

                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {error}
                  </div>
                )}

                <Button
                  variant="primary"
                  size="lg"
                  className="w-full"
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? 'Analyzing...' : 'Analyze Prompt'}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-2">
            {result ? (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Threat Classification</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-slate-600 mb-2">Category</p>
                        <p className="text-xl font-semibold text-slate-900">{result.category}</p>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-slate-600 mb-1">Risk Score</p>
                          <div className="flex items-center gap-2">
                            <div className="text-2xl font-bold text-slate-900">{result.risk_score.toFixed(1)}</div>
                            <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center text-xs font-semibold">
                              {(result.risk_score).toFixed(0)}%
                            </div>
                          </div>
                        </div>

                        <div>
                          <p className="text-sm text-slate-600 mb-1">Severity</p>
                          <Badge variant={getSeverityColor(result.severity)}>
                            {result.severity}
                          </Badge>
                        </div>
                      </div>

                      <div>
                        <p className="text-sm text-slate-600 mb-1">Confidence</p>
                        <p className="text-lg font-semibold text-slate-900">
                          {(result.confidence * 100).toFixed(1)}%
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-600 mb-1">Decision</p>
                        <Badge variant={getDecisionColor(result.decision)}>
                          {result.decision}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Explanation</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm text-slate-600 mb-2">Classification Reason</p>
                        <p className="text-slate-700 text-sm">{result.classification_reason}</p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-600 mb-2">Threat Explanation</p>
                        <p className="text-slate-700 text-sm">{result.threat_explanation}</p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-600 mb-2">Policy Rule</p>
                        <p className="text-slate-700 text-sm font-mono text-xs bg-slate-50 p-2 rounded">
                          {result.policy_rule_triggered}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {result.decision === 'ALLOW' && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Answer</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {result.llm_response ? (
                        <>
                          <div className="bg-slate-50 p-4 rounded-lg">
                            <div
                              className="text-sm text-slate-700"
                              dangerouslySetInnerHTML={{ __html: formatMarkdown(result.llm_response) }}
                            />
                          </div>
                          <p className="text-xs text-slate-500 mt-2">
                            Provider: {result.llm_provider} | Latency: {result.latency_ms?.toFixed(0)}ms
                          </p>
                        </>
                      ) : (
                        <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                          <p className="text-sm text-red-700">
                            The prompt was allowed, but the LLM call failed
                            {result.llm_error ? `: ${result.llm_error}` : '.'}
                          </p>
                          <p className="text-xs text-red-500 mt-1">
                            Check the backend's GEMINI_API_KEY and GEMINI_MODEL_NAME in .env.
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : (
              <Card>
                <CardContent className="text-center py-12">
                  <p className="text-slate-600">Enter a prompt and click analyze to see the results here.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}