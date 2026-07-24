import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'
import { GlassCard } from './GlassCard'
import { AnimatedCounter } from '../visualization/AnimatedCounter'

interface MetricCardProps {
  icon: LucideIcon
  title: string
  value: number
  suffix?: string
  prefix?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  delay?: number
  className?: string
}

export const MetricCard = ({
  icon: Icon,
  title,
  value,
  suffix = '',
  prefix = '',
  trend = 'neutral',
  trendValue = '',
  delay = 0,
  className = '',
}: MetricCardProps) => {
  const trendColor =
    trend === 'up'
      ? 'text-cyan-400'
      : trend === 'down'
        ? 'text-red-400'
        : 'text-cyan-400'

  return (
    <GlassCard delay={delay} className={`p-6 md:p-8 ${className}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 rounded-lg bg-cyan-500/10 backdrop-blur border border-cyan-500/20">
          <Icon className="w-6 h-6 text-cyan-400" />
        </div>
        {trendValue && (
          <span className={`text-sm font-semibold ${trendColor}`}>{trendValue}</span>
        )}
      </div>

      <AnimatedCounter
        value={value}
        label={title}
        suffix={suffix}
        prefix={prefix}
        delay={delay + 0.2}
      />
    </GlassCard>
  )
}
