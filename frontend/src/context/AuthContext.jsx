import { createContext, useState, useCallback, useEffect } from 'react'
import { authAPI } from '../api/client'

export const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [refreshToken, setRefreshToken] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isInitialized, setIsInitialized] = useState(false) // ← NEW: Track initialization

  // Restore from localStorage on mount
  useEffect(() => {
    console.log('AuthProvider: Initializing...')
    try {
      const stored = localStorage.getItem('authToken')
      const storedRefresh = localStorage.getItem('refreshToken')
      
      if (stored && storedRefresh) {
        console.log('AuthProvider: Restoring tokens from localStorage')
        setToken(stored)
        setRefreshToken(storedRefresh)
      } else {
        console.log('AuthProvider: No tokens in localStorage')
      }
    } catch (err) {
      console.error('AuthProvider: Error restoring auth', err)
    } finally {
      // Mark as initialized regardless of whether tokens exist
      setIsInitialized(true)
      console.log('AuthProvider: Initialization complete')
    }
  }, [])

  const register = useCallback(async (email, password, fullName) => {
    setLoading(true)
    setError(null)
    try {
      console.log('AuthProvider: Registering user', email)
      const response = await authAPI.register(email, password, fullName)
      const { access_token, refresh_token, user: userData } = response.data
      setToken(access_token)
      setRefreshToken(refresh_token)
      setUser(userData)
      localStorage.setItem('authToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      console.log('AuthProvider: Registration successful')
      return { success: true }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Registration failed'
      console.error('AuthProvider: Registration error', msg)
      setError(msg)
      return { success: false, error: msg }
    } finally {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    setLoading(true)
    setError(null)
    try {
      console.log('AuthProvider: Logging in user', email)
      const response = await authAPI.login(email, password)
      const { access_token, refresh_token, user: userData } = response.data
      setToken(access_token)
      setRefreshToken(refresh_token)
      setUser(userData)
      localStorage.setItem('authToken', access_token)
      localStorage.setItem('refreshToken', refresh_token)
      console.log('AuthProvider: Login successful')
      return { success: true }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Login failed'
      console.error('AuthProvider: Login error', msg)
      setError(msg)
      return { success: false, error: msg }
    } finally {
      setLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    console.log('AuthProvider: Logging out')
    setUser(null)
    setToken(null)
    setRefreshToken(null)
    localStorage.removeItem('authToken')
    localStorage.removeItem('refreshToken')
  }, [])

  const value = {
    user,
    token,
    refreshToken,
    loading,
    error,
    register,
    login,
    logout,
    isAuthenticated: !!token,
    isInitialized, // ← NEW: Export initialization status
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}