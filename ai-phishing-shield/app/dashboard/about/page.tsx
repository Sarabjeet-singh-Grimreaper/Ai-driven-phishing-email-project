'use client'

import { motion } from 'framer-motion'
import { Shield, Zap, TrendingUp, Users } from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'

export default function AboutPage() {
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
          About AI Phishing Shield
        </h1>
        <p className="text-muted-foreground">
          Enterprise-grade AI-powered phishing detection and email security
        </p>
      </motion.div>

      {/* Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <GlassCard className="p-8">
          <h2 className="text-2xl font-display font-bold mb-4">Our Mission</h2>
          <p className="text-muted-foreground leading-relaxed">
            AI Phishing Shield is dedicated to protecting organizations from sophisticated email
            threats through advanced machine learning and behavioral analysis. We combine
            cutting-edge AI technology with human expertise to deliver industry-leading phishing
            detection accuracy and zero-day threat prevention. Our mission is to make enterprise
            email security accessible, reliable, and effective for organizations of all sizes.
          </p>
        </GlassCard>
      </motion.div>

      {/* Key Stats */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15 }}
      >
        {[
          { label: 'Detection Accuracy', value: '98.1%', icon: TrendingUp },
          { label: 'Enterprise Clients', value: '1000+', icon: Users },
          { label: 'Daily Scans', value: '50M+', icon: Shield },
          { label: 'Response Time', value: '245ms', icon: Zap },
        ].map((stat, idx) => {
          const Icon = stat.icon
          return (
            <GlassCard key={idx} delay={0.2 + idx * 0.05} className="p-6">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 rounded-lg bg-gradient-cyan-purple/10">
                  <Icon className="w-5 h-5 text-cyan-400" />
                </div>
              </div>
              <p className="text-2xl font-display font-bold gradient-text">{stat.value}</p>
              <p className="text-xs text-muted-foreground mt-2">{stat.label}</p>
            </GlassCard>
          )
        })}
      </motion.div>

      {/* Technology Stack */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-6">Machine Learning Models</h3>
          <ul className="space-y-3">
            {[
              'Advanced CNN-LSTM Ensemble (Production)',
              'Transformer-BERT Architecture (Testing)',
              'Gradient Boosting Classifier',
              'Real-time Anomaly Detection',
            ].map((item, idx) => (
              <motion.li
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.35 + idx * 0.05 }}
                className="flex items-center gap-3 text-sm"
              >
                <span className="w-2 h-2 rounded-full bg-cyan-400" />
                {item}
              </motion.li>
            ))}
          </ul>
        </GlassCard>

        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-6">Detection Features</h3>
          <ul className="space-y-3">
            {[
              'Email Header Analysis',
              'URL Reputation Scanning',
              'Credential Harvesting Detection',
              'Domain Spoofing Prevention',
              'Urgency Language Recognition',
              'Attachment Malware Scanning',
            ].map((item, idx) => (
              <motion.li
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.4 + idx * 0.05 }}
                className="flex items-center gap-3 text-sm"
              >
                <span className="w-2 h-2 rounded-full bg-purple-400" />
                {item}
              </motion.li>
            ))}
          </ul>
        </GlassCard>
      </motion.div>

      {/* Architecture */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-6">System Architecture</h3>
          <div className="space-y-4">
            {[
              { title: 'Intake Layer', desc: 'IMAP/API email ingestion with SSL/TLS encryption' },
              { title: 'Feature Extraction', desc: 'Parallel processing of headers, content, and URLs' },
              { title: 'ML Pipeline', desc: 'Ensemble model prediction with confidence scoring' },
              { title: 'Decision Engine', desc: 'Rule-based post-processing and risk assessment' },
              { title: 'Storage', desc: 'Encrypted database with audit logging and retention policies' },
              { title: 'API Gateway', desc: 'RESTful API with rate limiting and authentication' },
            ].map((component, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.55 + idx * 0.05 }}
                className="flex items-start gap-4 p-4 rounded-lg bg-white/5 border border-white/10"
              >
                <span className="text-cyan-400 font-bold">→</span>
                <div>
                  <p className="font-semibold text-sm">{component.title}</p>
                  <p className="text-xs text-muted-foreground mt-1">{component.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </GlassCard>
      </motion.div>

      {/* Security & Compliance */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.7 }}
      >
        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-4">Security Standards</h3>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              ISO 27001 Certified
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              SOC 2 Type II Compliant
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              GDPR & CCPA Compliant
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              99.9% Uptime SLA
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400" />
              End-to-End Encryption
            </li>
          </ul>
        </GlassCard>

        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-4">Performance Metrics</h3>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li className="flex items-center justify-between">
              <span>Detection Accuracy</span>
              <span className="text-cyan-400 font-semibold">98.1%</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Precision Rate</span>
              <span className="text-cyan-400 font-semibold">97.2%</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Recall Rate</span>
              <span className="text-cyan-400 font-semibold">98.7%</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Avg Response Time</span>
              <span className="text-cyan-400 font-semibold">245ms</span>
            </li>
            <li className="flex items-center justify-between">
              <span>Daily Threat Coverage</span>
              <span className="text-cyan-400 font-semibold">99.2%</span>
            </li>
          </ul>
        </GlassCard>
      </motion.div>

      {/* Version & Credits */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.85 }}
        className="text-center text-sm text-muted-foreground border-t border-white/10 pt-8"
      >
        <p>AI Phishing Shield v1.0</p>
        <p className="mt-2">
          Built with advanced machine learning, enterprise security, and cutting-edge AI
          technology
        </p>
      </motion.div>
    </motion.div>
  )
}
