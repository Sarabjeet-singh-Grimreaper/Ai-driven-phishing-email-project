import { motion } from 'framer-motion'

interface StatusChipProps {
  status: 'safe' | 'warning' | 'danger'
  label: string
  delay?: number
}

export const StatusChip = ({ status, label, delay = 0 }: StatusChipProps) => {
  const statusColors = {
    safe: 'bg-green-500/20 text-green-400 border-green-500/50',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    danger: 'bg-red-500/20 text-red-400 border-red-500/50',
  }

  const dotColors = {
    safe: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500',
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3, delay }}
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border glass-dark ${statusColors[status]}`}
    >
      <div className={`w-2 h-2 rounded-full ${dotColors[status]} animate-pulse`} />
      <span className="text-xs font-semibold">{label}</span>
    </motion.div>
  )
}
