import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Shield } from 'lucide-react'

export function ProtectedRoute({ children }) {
  const auth = useAuth()
  const { isAuthenticated, isInitialized } = auth

  console.log('ProtectedRoute: Checking auth', { isAuthenticated, isInitialized })

  // Wait for auth to initialize
  if (!isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 mb-4 animate-spin">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <p className="text-slate-400 mt-4">Loading...</p>
        </div>
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    console.log('ProtectedRoute: Not authenticated, redirecting to login')
    return <Navigate to="/login" replace />
  }

  // User is authenticated, render children
  return children
}