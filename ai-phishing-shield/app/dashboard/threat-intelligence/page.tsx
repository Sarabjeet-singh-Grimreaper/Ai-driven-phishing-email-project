'use client'

import { motion } from 'framer-motion'
import {
  AlertTriangle,
  Globe,
  Shield,
  TrendingUp,
  Lock,
  Eye,
} from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'
import { ThreatBadge } from '@/components/cards/ThreatBadge'
import { StatusChip } from '@/components/cards/StatusChip'

const threatLevels = [
  {
    label: 'Threat Level',
    icon: AlertTriangle,
    value: 'CRITICAL',
    description: 'Multiple threat indicators detected',
    severity: 'critical' as const,
  },
  {
    label: 'Attack Type',
    icon: TrendingUp,
    value: 'Credential Phishing',
    description: 'Targeting user credentials',
    severity: 'high' as const,
  },
  {
    label: 'Sender Reputation',
    icon: Eye,
    value: 'Malicious',
    description: 'Known phishing domain',
    severity: 'critical' as const,
  },
  {
    label: 'Risk Score',
    icon: Shield,
    value: '96/100',
    description: 'Extremely high risk',
    severity: 'critical' as const,
  },
]

const indicators = [
  { label: 'MFA Bypass Attempt', value: 'Detected', severity: 'critical' as const },
  { label: 'Domain Spoofing', value: 'Detected', severity: 'high' as const },
  { label: 'Urgency Language', value: 'Detected', severity: 'high' as const },
  { label: 'Suspicious Links', value: '3 Found', severity: 'critical' as const },
  { label: 'HTML Obfuscation', value: 'Detected', severity: 'medium' as const },
  { label: 'Request for Sensitive Data', value: 'Detected', severity: 'high' as const },
]

export default function ThreatIntelligencePage() {
  return (
    <motion.div
      className="space-y-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl md:text-4xl font-display font-bold gradient-text mb-2">
          Threat Intelligence
        </h1>
        <p className="text-muted-foreground">Detailed threat analysis and indicators</p>
      </motion.div>

      {/* Threat Assessment Grid */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        {threatLevels.map((item, idx) => {
          const Icon = item.icon
          return (
            <GlassCard key={idx} delay={0.1 + idx * 0.05} className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-lg bg-gradient-cyan-purple/10">
                  <Icon className="w-6 h-6 text-cyan-400" />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-muted-foreground mb-1">{item.label}</p>
                  <p className="text-lg font-display font-bold mb-1">{item.value}</p>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
              </div>
            </GlassCard>
          )
        })}
      </motion.div>

      {/* Threat Indicators */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.25 }}
      >
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-6">Threat Indicators</h2>

          <div className="space-y-3">
            {indicators.map((indicator, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.3 + idx * 0.05 }}
                className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
              >
                <span className="font-semibold text-sm">{indicator.label}</span>
                <StatusChip
                  status={
                    indicator.severity === 'critical'
                      ? 'danger'
                      : indicator.severity === 'high'
                        ? 'warning'
                        : 'warning'
                  }
                  label={indicator.value}
                />
              </motion.div>
            ))}
          </div>
        </GlassCard>
      </motion.div>

      {/* Recommendations */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Immediate Actions
          </h3>
          <ul className="space-y-3 text-sm">
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Do not click any links in the email</span>
            </li>
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Do not provide personal or financial information</span>
            </li>
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Report email to IT security immediately</span>
            </li>
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Delete the email from your inbox</span>
            </li>
          </ul>
        </GlassCard>

        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-green-400" />
            Prevention Tips
          </h3>
          <ul className="space-y-3 text-sm">
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Enable multi-factor authentication (MFA)</span>
            </li>
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Use strong, unique passwords</span>
            </li>
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Verify sender email addresses carefully</span>
            </li>
            <li className="flex gap-3">
              <span className="text-cyan-400 font-bold">•</span>
              <span>Use email filtering and security tools</span>
            </li>
          </ul>
        </GlassCard>
      </motion.div>
    </motion.div>
  )
}
