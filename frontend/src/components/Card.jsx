export function Card({ children, className = '', hover = true }) {
  return (
    <div className={`
      glass-effect rounded-xl p-6 border border-slate-200
      ${hover ? 'card-hover' : ''} 
      ${className}
    `}>
      {children}
    </div>
  )
}

export function CardHeader({ children, className = '' }) {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className = '' }) {
  return (
    <h3 className={`text-lg font-bold text-slate-900 ${className}`}>
      {children}
    </h3>
  )
}

export function CardContent({ children, className = '' }) {
  return (
    <div className={className}>
      {children}
    </div>
  )
}