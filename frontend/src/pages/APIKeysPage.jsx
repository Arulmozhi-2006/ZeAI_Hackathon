import { useState, useEffect } from 'react'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { Badge } from '../components/Badge'
import { useAuth } from '../hooks/useAuth'
import { apiKeysAPI } from '../api/client'
import { Copy, Trash2, Plus, Eye, EyeOff } from 'lucide-react'

export function APIKeysPage() {
  const { token } = useAuth()
  const [keys, setKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [showNew, setShowNew] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyData, setNewKeyData] = useState(null)
  const [showRawKey, setShowRawKey] = useState(false)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    fetchKeys()
  }, [token])

  const fetchKeys = async () => {
    try {
      setLoading(true)
      const response = await apiKeysAPI.list(token)
      setKeys(response.data)
    } catch (err) {
      console.error('Failed to load API keys:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateKey = async (e) => {
    e.preventDefault()
    if (!newKeyName.trim()) {
      alert('Please enter a name')
      return
    }

    try {
      const response = await apiKeysAPI.create(newKeyName, null, token)
      setNewKeyData(response.data)
      setNewKeyName('')
      setShowNew(false)
      fetchKeys()
    } catch (err) {
      console.error('Failed to create API key:', err)
      alert('Failed to create API key')
    }
  }

  const handleCopyKey = () => {
    if (newKeyData?.raw_key) {
      navigator.clipboard.writeText(newKeyData.raw_key)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleRevokeKey = async (keyId) => {
    if (!confirm('Are you sure you want to revoke this key?')) return

    try {
      await apiKeysAPI.revoke(keyId, token)
      fetchKeys()
    } catch (err) {
      console.error('Failed to revoke key:', err)
      alert('Failed to revoke key')
    }
  }

  return (
    <Layout>
      <div>
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900">API Keys</h1>
            <p className="text-slate-600 mt-2">Manage your API keys for programmatic access</p>
          </div>
          <Button variant="primary" onClick={() => setShowNew(!showNew)}>
            <Plus className="w-4 h-4" />
            New Key
          </Button>
        </div>

        {/* New Key Form */}
        {showNew && (
          <Card className="mb-8 animate-fade-in-up">
            <CardHeader>
              <CardTitle>Create New API Key</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateKey} className="space-y-4">
                <Input
                  label="Key Name"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder="e.g., Production Server"
                  required
                />
                <Button type="submit" variant="primary">Create Key</Button>
              </form>
            </CardContent>
          </Card>
        )}

        {/* New Key Display */}
        {newKeyData && (
          <Card className="mb-8 border-emerald-200 bg-emerald-50 animate-fade-in-up">
            <CardHeader>
              <CardTitle className="text-emerald-900">✓ API Key Created</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-emerald-800 mb-4">
                Save this key somewhere safe. You won't be able to see it again.
              </p>
              <div className="bg-white p-4 rounded-lg border border-emerald-200 mb-4 flex items-center justify-between">
                <code className="text-sm font-mono text-slate-700 break-all">
                  {showRawKey ? newKeyData.raw_key : '••••••••••••••••••••'}
                </code>
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowRawKey(!showRawKey)}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    {showRawKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={handleCopyKey}
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-600 mb-4 bg-slate-50 p-3 rounded">
                <strong>Example usage:</strong><br />
                <code>curl -H "X-API-Key: {newKeyData.raw_key}" http://localhost:8000/api/v1/firewall/analyze</code>
              </p>
              <Button variant="secondary" onClick={() => setNewKeyData(null)}>Done</Button>
            </CardContent>
          </Card>
        )}

        {/* Keys List */}
        <div className="space-y-4">
          {loading ? (
            <Card>
              <div className="h-32 bg-slate-100 rounded animate-pulse" />
            </Card>
          ) : keys.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-slate-600">No API keys yet</p>
                <p className="text-sm text-slate-500 mt-1">Create one to get started</p>
              </CardContent>
            </Card>
          ) : (
            keys.map(key => (
              <Card key={key.id} className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-900">{key.name}</h3>
                  <div className="flex items-center gap-4 mt-2">
                    <p className="text-sm text-slate-600">
                      <code className="bg-slate-100 px-2 py-1 rounded">{key.key_prefix}...</code>
                    </p>
                    <Badge variant="blue">
                      {key.is_active ? '✓ Active' : '✗ Revoked'}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    Created {new Date(key.created_at).toLocaleDateString()}
                    {key.last_used_at && ` • Last used ${new Date(key.last_used_at).toLocaleDateString()}`}
                  </p>
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleRevokeKey(key.id)}
                  disabled={!key.is_active}
                >
                  <Trash2 className="w-4 h-4" />
                  Revoke
                </Button>
              </Card>
            ))
          )}
        </div>
      </div>
    </Layout>
  )
}