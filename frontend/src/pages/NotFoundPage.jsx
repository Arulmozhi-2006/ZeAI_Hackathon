import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/Button'

export const NotFoundPage = () => (
  <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
    <div className="text-center">
      <h1 className="text-6xl font-bold text-slate-900 mb-2">404</h1>
      <p className="text-xl text-slate-600 mb-8">Page not found</p>
      <Link to="/dashboard">
        <Button variant="primary">Back to Dashboard</Button>
      </Link>
    </div>
  </div>
)