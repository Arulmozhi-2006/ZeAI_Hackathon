export function Badge({ 
  children, 
  variant = 'slate', 
  className = '' 
}) {
  const variants = {
    slate: 'bg-slate-800 text-slate-100 border border-slate-700',
    green: 'bg-emerald-950 text-emerald-300 border border-emerald-800',
    yellow: 'bg-amber-950 text-amber-300 border border-amber-800',
    red: 'bg-red-950 text-red-300 border border-red-800',
    blue: 'bg-blue-950 text-blue-300 border border-blue-800',
    purple: 'bg-purple-950 text-purple-300 border border-purple-800',
  }

  return (
    <span className={`
      inline-flex items-center gap-2 
      px-3 py-1 rounded-full 
      text-sm font-medium 
      ${variants[variant]} 
      ${className}
    `}>
      {children}
    </span>
  )
}