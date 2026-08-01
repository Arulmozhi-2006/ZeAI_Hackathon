import { useState, useEffect } from 'react'
import { Layout } from '../components/Layout'
import { Card, CardHeader, CardTitle, CardContent } from '../components/Card'
import { Button } from '../components/Button'
import { Input } from '../components/Input'
import { Badge } from '../components/Badge'
import { useAuth } from '../hooks/useAuth'
import { apiKeysAPI } from '../api/client'
import { Bell, Shield, Lock, LogOut, KeyRound, Copy, Trash2, Plus, Eye, EyeOff } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function SettingsPage() {
  const { user, logout, token } = useAuth()
  const navigate = useNavigate()

  const [preferences, setPreferences] = useState({
    emailNotifications: true,
    threatAlerts: true,
    weeklyReport: true,
  })

  // Password change state
  const [showPasswordForm, setShowPasswordForm] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')

  // API keys state
  const [apiKeys, setApiKeys] = useState([])
  const [keysLoading, setKeysLoading] = useState(true)
  const [showNewKeyForm, setShowNewKeyForm] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newKeyData, setNewKeyData] = useState(null)
  const [showRawKey, setShowRawKey] = useState(false)

  useEffect(() => {
    fetchApiKeys()
  }, [token])

  const fetchApiKeys = async () => {
    try {
      setKeysLoading(true)
      const response = await apiKeysAPI.list(token)
      setApiKeys(response.data)
    } catch (err) {
      console.error('Failed to load API keys:', err)
    } finally {
      setKeysLoading(false)
    }
  }

  const handleCreateApiKey = async (e) => {
    e.preventDefault()
    if (!newKeyName.trim()) {
      alert('Please enter a name')
      return
    }
    try {
      const response = await apiKeysAPI.create(newKeyName, null, token)
      setNewKeyData(response.data)
      setNewKeyName('')
      setShowNewKeyForm(false)
      fetchApiKeys()
    } catch (err) {
      console.error('Failed to create API key:', err)
      alert('Failed to create API key')
    }
  }

  const handleCopyApiKey = () => {
    if (newKeyData?.raw_key) {
      navigator.clipboard.writeText(newKeyData.raw_key)
    }
  }

  const handleRevokeApiKey = async (keyId) => {
    if (!confirm('Are you sure you want to revoke this key?')) return
    try {
      await apiKeysAPI.revoke(keyId, token)
      fetchApiKeys()
    } catch (err) {
      console.error('Failed to revoke key:', err)
      alert('Failed to revoke key')
    }
  }

  const handleToggle = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  const handleChangePassword = async (e) => {
    e.preventDefault()
    setPasswordError('')
    setPasswordSuccess('')

    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError('All fields are required')
      return
    }

    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters')
      return
    }

    if (newPassword !== confirmPassword) {
      setPasswordError('Passwords do not match')
      return
    }

    if (newPassword === currentPassword) {
      setPasswordError('New password must be different from current password')
      return
    }

    try {
      setPasswordSuccess('✓ Password changed successfully')

      setTimeout(() => {
        setShowPasswordForm(false)
        setCurrentPassword('')
        setNewPassword('')
        setConfirmPassword('')
        setPasswordSuccess('')
      }, 1500)
    } catch (err) {
      setPasswordError('Failed to change password')
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <Layout>
      <div>
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900">Settings</h1>
          <p className="text-slate-600 mt-2">Manage your account and preferences</p>
        </div>

        <div className="space-y-6">

          {/* Profile Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-blue-600" />
                Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Full Name
                  </label>
                  <Input
                    value={user?.full_name || 'Kim'}
                    disabled
                    className="bg-slate-100 text-slate-700"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Email
                  </label>
                  <Input
                    value={user?.email || 'kim@gmail.com'}
                    disabled
                    className="bg-slate-100 text-slate-700"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Role
                </label>
                <div className="px-4 py-2.5 rounded-lg bg-slate-100 border border-slate-200">
                  <span className="text-slate-700 font-medium capitalize">
                    {user?.role || 'viewer'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Notifications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5 text-blue-600" />
                Notifications
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
              {[
                { key: 'emailNotifications', label: 'Email Notifications', desc: 'Receive updates via email' },
                { key: 'threatAlerts', label: 'Threat Alerts', desc: 'Get notified of high-risk threats' },
                { key: 'weeklyReport', label: 'Weekly Report', desc: 'Receive weekly security summary' },
              ].map(item => (
                <div
                  key={item.key}
                  className="flex items-center justify-between p-4 rounded-lg bg-slate-50 hover:bg-slate-100 transition-colors"
                >
                  <div>
                    <p className="font-medium text-slate-900">{item.label}</p>
                    <p className="text-sm text-slate-600">{item.desc}</p>
                  </div>

                  <button
                    onClick={() => handleToggle(item.key)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${preferences[item.key] ? 'bg-blue-600' : 'bg-slate-300'}`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${preferences[item.key] ? 'translate-x-6' : 'translate-x-1'}`}
                    />
                  </button>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* API Keys */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <KeyRound className="w-5 h-5 text-blue-600" />
                  API Keys
                </span>
                <Button size="sm" variant="primary" onClick={() => setShowNewKeyForm(!showNewKeyForm)}>
                  <Plus className="w-4 h-4" />
                  New Key
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-slate-600 -mt-2">
                Manage API keys used for programmatic access to the firewall.
              </p>

              {showNewKeyForm && (
                <form onSubmit={handleCreateApiKey} className="p-4 bg-slate-50 rounded-lg space-y-3">
                  <Input
                    label="Key Name"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    placeholder="e.g., Production Server"
                    required
                  />
                  <div className="flex gap-2">
                    <Button type="submit" size="sm">Create Key</Button>
                    <Button type="button" variant="secondary" size="sm" onClick={() => setShowNewKeyForm(false)}>
                      Cancel
                    </Button>
                  </div>
                </form>
              )}

              {newKeyData && (
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                  <p className="text-sm text-emerald-800 mb-3">
                    ✓ Key created. Save it now — you won't be able to see it again.
                  </p>
                  <div className="bg-white p-3 rounded-lg border border-emerald-200 flex items-center justify-between">
                    <code className="text-sm font-mono text-slate-700 break-all">
                      {showRawKey ? newKeyData.raw_key : '••••••••••••••••••••'}
                    </code>
                    <div className="flex gap-1 shrink-0 ml-2">
                      <button
                        type="button"
                        onClick={() => setShowRawKey(!showRawKey)}
                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                      >
                        {showRawKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button
                        type="button"
                        onClick={handleCopyApiKey}
                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <Button variant="secondary" size="sm" className="mt-3" onClick={() => setNewKeyData(null)}>
                    Done
                  </Button>
                </div>
              )}

              <div className="space-y-3">
                {keysLoading ? (
                  <div className="h-16 bg-slate-100 rounded animate-pulse" />
                ) : apiKeys.length === 0 ? (
                  <p className="text-sm text-slate-500 text-center py-4">No API keys yet</p>
                ) : (
                  apiKeys.map(key => (
                    <div
                      key={key.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-50"
                    >
                      <div>
                        <p className="font-medium text-slate-900 text-sm">{key.name}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <code className="text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                            {key.key_prefix}...
                          </code>
                          <Badge variant="blue">{key.is_active ? 'Active' : 'Revoked'}</Badge>
                        </div>
                      </div>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleRevokeApiKey(key.id)}
                        disabled={!key.is_active}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Security */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="w-5 h-5 text-blue-600" />
                Security
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">

              {/* Change Password */}
              {!showPasswordForm ? (
                <Button
                  variant="secondary"
                  className="w-full"
                  onClick={() => setShowPasswordForm(true)}
                >
                  Change Password
                </Button>
              ) : (
                <div className="p-4 bg-slate-50 rounded-lg space-y-4">
                  <h4 className="font-semibold text-slate-900">
                    Change Your Password
                  </h4>

                  {passwordError && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                      {passwordError}
                    </div>
                  )}

                  {passwordSuccess && (
                    <div className="p-3 bg-emerald-50 border border-emerald-200 rounded text-sm text-emerald-700">
                      {passwordSuccess}
                    </div>
                  )}

                  <form onSubmit={handleChangePassword} className="space-y-3">

                    <Input
                      label="Current Password"
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />

                    <Input
                      label="New Password"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />

                    <Input
                      label="Confirm Password"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />

                    <div className="flex gap-2">
                      <Button type="submit" size="sm">
                        Update Password
                      </Button>

                      <Button
                        type="button"
                        variant="secondary"
                        size="sm"
                        onClick={() => setShowPasswordForm(false)}
                      >
                        Cancel
                      </Button>
                    </div>

                  </form>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-900">
                <LogOut className="w-5 h-5" />
                Danger Zone
              </CardTitle>
            </CardHeader>

            <CardContent>
              <Button variant="danger" onClick={handleLogout}>
                Log Out
              </Button>
            </CardContent>
          </Card>

        </div>
      </div>
    </Layout>
  )
}