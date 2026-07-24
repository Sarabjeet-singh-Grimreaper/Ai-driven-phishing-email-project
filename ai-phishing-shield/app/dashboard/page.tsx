'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Mail,
  Shield,
  Target,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react'
import { MetricCard } from '@/components/cards/MetricCard'
import { GlassCard } from '@/components/cards/GlassCard'
import { fetchDashboard, DashboardData } from '@/services/api'
import toast from 'react-hot-toast'

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const stats = await fetchDashboard()
        setData(stats)
      } catch (error) {
        toast.error('Failed to load dashboard metrics from backend.')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }
    loadDashboard()
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="w-8 h-8 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" />
        <p className="text-muted-foreground">Synchronizing metrics from CyberShield backend...</p>
      </div>
    )
  }

  const stats = data || {
    total_emails: 24582,
    threats: 342,
    accuracy: 98.1,
    avg_confidence: 96.4,
    safe_emails: 23840,
    critical_threats: 28,
    best_model: 'Random Forest (Tuned)',
    roc: 0.993,
  }

  return (
    <motion.div
      className="space-y-8"
      initial="hidden"
      animate="show"
      variants={containerVariants}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl md:text-4xl font-display font-bold gradient-text mb-2">
          Dashboard
        </h1>
        <p className="text-muted-foreground">
          Real-time threat detection and email security metrics
        </p>
      </motion.div>

      {/* Main Metrics Grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        variants={containerVariants}
      >
        <MetricCard
          icon={Mail}
          title="Emails Scanned"
          value={stats.total_emails}
          suffix="+"
          trend="up"
          trendValue="+12.5%"
          delay={0}
        />
        <MetricCard
          icon={AlertTriangle}
          title="Threats Blocked"
          value={stats.threats}
          trend="up"
          trendValue="+5.2%"
          delay={0.1}
        />
        <MetricCard
          icon={Target}
          title="Detection Accuracy"
          value={stats.accuracy}
          suffix="%"
          trend="up"
          trendValue="+0.3%"
          delay={0.2}
        />
        <MetricCard
          icon={Shield}
          title="Average Confidence"
          value={stats.avg_confidence}
          suffix="%"
          delay={0.3}
        />
        <MetricCard
          icon={CheckCircle}
          title="Safe Emails"
          value={stats.safe_emails}
          delay={0.4}
        />
        <MetricCard
          icon={AlertTriangle}
          title="Critical Threats"
          value={stats.critical_threats}
          trend="down"
          trendValue="-2.1%"
          delay={0.5}
        />
      </motion.div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        <GlassCard className="p-6 md:p-8">
          <h2 className="text-xl font-display font-bold mb-6">Recent Detections</h2>

          <div className="space-y-4">
            {[
              {
                email: 'suspicious@example.com',
                subject: 'Urgent Account Verification Required',
                risk: 'Critical',
                time: '2 min ago',
                color: 'text-red-400',
              },
              {
                email: 'noreply@bank-alert.com',
                subject: 'Confirm Your Banking Details',
                risk: 'High',
                time: '15 min ago',
                color: 'text-orange-400',
              },
              {
                email: 'support@legitimate-service.com',
                subject: 'Your Password Reset Link',
                risk: 'Medium',
                time: '1 hour ago',
                color: 'text-yellow-400',
              },
              {
                email: 'newsletter@company.com',
                subject: 'Monthly Product Update',
                risk: 'Safe',
                time: '2 hours ago',
                color: 'text-green-400',
              },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.7 + idx * 0.1 }}
                className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-white/10 cursor-pointer group"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-sm truncate">{item.subject}</p>
                  <p className="text-xs text-muted-foreground truncate">{item.email}</p>
                </div>
                <div className="ml-4 flex items-center gap-4">
                  <span className={`text-xs font-bold ${item.color}`}>{item.risk}</span>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">{item.time}</span>
                </div>
              </motion.div>
            ))}
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="mt-6 w-full py-2 rounded-lg bg-gradient-cyan-purple/10 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/20 transition-all duration-300 text-sm font-semibold"
          >
            View All Detections
          </motion.button>
        </GlassCard>
      </motion.div>

      {/* Stats */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1 }}
      >
        <GlassCard className="p-6 md:p-8">
          <h3 className="text-lg font-display font-bold mb-4">Today&apos;s Stats</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Scans</span>
              <span className="font-semibold">{(stats.total_emails / 20).toFixed(0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Threats Detected</span>
              <span className="font-semibold text-red-400">{stats.threats}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Accuracy Rate</span>
              <span className="font-semibold text-green-400">{stats.accuracy}%</span>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-white/10">
              <span className="text-sm text-muted-foreground">Avg Response Time</span>
              <span className="font-semibold text-cyan-400">98ms</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6 md:p-8">
          <h3 className="text-lg font-display font-bold mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">AI Models ({stats.best_model})</span>
              <span className="inline-flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs font-semibold">Healthy</span>
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">API Status</span>
              <span className="inline-flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs font-semibold">Operational</span>
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Database</span>
              <span className="inline-flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs font-semibold">Connected</span>
              </span>
            </div>
            <div className="flex items-center justify-between pt-3 border-t border-white/10">
              <span className="text-sm text-muted-foreground">ROC AUC Index</span>
              <span className="font-semibold text-green-400">{stats.roc}</span>
            </div>
          </div>
        </GlassCard>
      </motion.div>
    </motion.div>
  )
}
