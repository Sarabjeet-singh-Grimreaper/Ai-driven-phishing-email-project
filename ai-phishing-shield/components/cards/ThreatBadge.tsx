import { LucideIcon } from 'lucide-react'
import { motion } from 'framer-motion'

interface ThreatBadgeProps {
  icon: LucideIcon
  title: string
  value?: string
  severity?: 'critical' | 'high' | 'medium' | 'low'
  delay?: number
}

export const ThreatBadge = ({
  icon: Icon,
  title,
  value,
  severity = 'medium',
  delay = 0,
}: ThreatBadgeProps) => {
  const severityColors = {
    critical: 'bg-red-500/20 text-red-300 border-red-500/50',
    high: 'bg-orange-500/20 text-orange-300 border-orange-500/50',
    medium: 'bg-amber-500/20 text-amber-300 border-amber-500/50',
    low: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50',
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay }}
      className={`glass-card p-4 border ${severityColors[severity]} backdrop-blur-xl`}
    >
      <div className="flex items-center gap-3">
        <Icon className="w-5 h-5" />
        <div className="flex-1">
          <p className="font-semibold text-sm">{title}</p>
          {value && <p className="text-xs opacity-75">{value}</p>}
        </div>
      </div>
    </motion.div>
  )
}
