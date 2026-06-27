import { useState, useEffect } from 'react'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { Badge } from '../components/Badge'
import { useAuth } from '../hooks/useAuth'
import { analyticsAPI } from '../api/client'
import { TrendingUp, Shield, AlertCircle, CheckCircle2 } from 'lucide-react'

function StatCard({ icon: Icon, label, value, unit = '', trend = null }) {
  return (
    <Card hover className="group">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-slate-600 mb-2">{label}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold text-slate-900">{value}</span>
            {unit && <span className="text-sm text-slate-600">{unit}</span>}
          </div>
          {trend && (
            <div className="mt-2 flex items-center gap-1 text-sm text-emerald-600">
              <TrendingUp className="w-4 h-4" />
              {trend}
            </div>
          )}
        </div>
        <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center group-hover:scale-110 transition-transform">
          <Icon className="w-6 h-6 text-blue-600" />
        </div>
      </div>
    </Card>
  )
}

export function DashboardPage() {
  const { token } = useAuth()
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const response = await analyticsAPI.getOverview(30, token)
        setOverview(response.data)
      } catch (err) {
        console.error('Failed to load overview:', err)
      } finally {
        setLoading(false)
      }
    }

    if (token) {
      fetchOverview()
    }
  }, [token])

  const data = overview || {}

  return (
    <Layout>
      <div>
        <div className="mb-12 animate-fade-in">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Dashboard</h1>
          <p className="text-slate-600">Monitor your firewall protection in real-time</p>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1,2,3,4].map(i => (
              <div key={i} className="h-32 bg-slate-200 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard 
              icon={Shield} 
              label="Total Requests" 
              value={data.total_requests || 0}
              trend="+12% from last month"
            />
            <StatCard 
              icon={CheckCircle2} 
              label="Allowed" 
              value={data.total_allowed || 0}
              unit="safe"
            />
            <StatCard 
              icon={AlertCircle} 
              label="Blocked" 
              value={data.total_blocked || 0}
              unit="threats"
            />
            <StatCard 
              icon={TrendingUp} 
              label="Block Rate" 
              value={data.block_rate || 0}
              unit="%"
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Welcome to the Firewall</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600 mb-6">
                Your AI security command center is live. Monitor adversarial prompts, analyze threat patterns, and protect your LLM from sophisticated attacks in real-time.
              </p>
              <div className="space-y-3">
                {[
                  'Advanced ML-powered threat detection',
                  'Real-time attack pattern analysis',
                  'Automated blocking of jailbreak attempts'
                ].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span className="text-slate-700">{feature}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <a href="/inspector" className="block p-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors text-sm font-medium text-slate-700">
                → Test Prompt
              </a>
              <a href="/logs" className="block p-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors text-sm font-medium text-slate-700">
                → View Logs
              </a>
              <a href="/analytics" className="block p-3 rounded-lg bg-blue-50 hover:bg-blue-100 transition-colors text-sm font-medium text-slate-700">
                → Analytics
              </a>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 p-6 rounded-xl bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-200 animate-fade-in-up">
          <div className="flex items-center gap-4">
            <Shield className="w-8 h-8 text-blue-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-slate-900 mb-1">Enterprise Features</h3>
              <p className="text-sm text-slate-700">Unlock advanced analytics, custom policies, and dedicated support with a plan upgrade.</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}