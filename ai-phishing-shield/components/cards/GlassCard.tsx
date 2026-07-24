import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hoverable?: boolean
  glow?: 'cyan' | 'crimson' | 'none'
  delay?: number
}

export const GlassCard = ({
  children,
  className = '',
  hoverable = true,
  glow = 'cyan',
  delay = 0,
}: GlassCardProps) => {
  const glowClass =
    glow === 'cyan'
      ? 'hover:shadow-xl hover:shadow-cyan-500/40'
      : glow === 'crimson'
        ? 'hover:shadow-xl hover:shadow-red-500/30'
        : ''

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`glass-card neo-depth ${hoverable ? `floating-card ${glowClass}` : ''} ${className}`}
    >
      {children}
    </motion.div>
  )
}
