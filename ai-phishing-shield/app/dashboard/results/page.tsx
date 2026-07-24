'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Link2,
  Lock,
  AlertCircle,
  CheckCircle2,
  Copy,
  Download,
  Share2,
  Mail,
  ArrowLeft,
} from 'lucide-react'
import { RiskMeter } from '@/components/visualization/RiskMeter'
import { ThreatBadge } from '@/components/cards/ThreatBadge'
import { StatusChip } from '@/components/cards/StatusChip'
import { GlassCard } from '@/components/cards/GlassCard'
import toast from 'react-hot-toast'
import { ScanResponse, getReportPdfUrl } from '@/services/api'

// Simple helper to assign Lucide Icons based on keywords
const getIconForIndicator = (indicator: string) => {
  const ind = indicator.toLowerCase()
  if (ind.includes('url') || ind.includes('link')) return Link2
  if (ind.includes('password') || ind.includes('credential') || ind.includes('login')) return Lock
  if (ind.includes('urgency') || ind.includes('immediate') || ind.includes('attention')) return AlertCircle
  if (ind.includes('tld') || ind.includes('domain') || ind.includes('spoof')) return Mail
  return AlertCircle
}

export default function ResultsPage() {
  const [result, setResult] = useState<ScanResponse | null>(null)
  const [rawEmail, setRawEmail] = useState<string>('')

  useEffect(() => {
    const storedResult = localStorage.getItem('shield_analysis_result')
    const storedEmail = localStorage.getItem('shield_email_source')
    if (storedResult) {
      setResult(JSON.parse(storedResult))
    }
    if (storedEmail) {
      setRawEmail(storedEmail)
    }
  }, [])

  const handleCopy = () => {
    navigator.clipboard.writeText(rawEmail)
    toast.success('Email copied to clipboard')
  }

  const handleDownloadReportText = () => {
    if (!result) return
    const reportText = `AI CYBERSHIELD PHISHING ANALYSIS REPORT\n` +
      `--------------------------------------\n` +
      `Prediction: ${result.prediction}\n` +
      `Confidence: ${result.confidence}%\n` +
      `Risk Score: ${result.risk_score}/100\n` +
      `Severity: ${result.severity}\n` +
      `Classification: ${result.attack_type}\n` +
      `Analyzed via Model: ${result.model}\n` +
      `Indicators:\n` +
      result.indicators.map(ind => ` - ${ind}`).join('\n')
      
    const element = document.createElement('a')
    const file = new Blob([reportText], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = 'analysis_report.txt'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
    toast.success('Report text downloaded')
  }

  const handleDownloadPdf = () => {
    // We open the backend PDF generation route directly
    const url = getReportPdfUrl('latest')
    window.open(url, '_blank')
    toast.success('Initiating PDF report download...')
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
        <p className="text-muted-foreground">Loading analysis results...</p>
      </div>
    )
  }

  const isPhishing = result.prediction === 'Phishing'

  return (
    <motion.div
      className="space-y-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with Back Button */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center gap-4"
      >
        <Link href="/dashboard/email-scanner">
          <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
        </Link>
        <div>
          <h1 className="text-3xl md:text-4xl font-display font-bold gradient-text mb-2">
            Analysis Results
          </h1>
          <p className="text-muted-foreground">Dynamic Engine Scan Summary</p>
        </div>
      </motion.div>

      {/* Risk Assessment */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
        className="flex flex-col md:flex-row gap-8 items-start"
      >
        {/* Risk Meter */}
        <div className="flex-1 flex justify-center">
          <RiskMeter score={result.risk_score} label="Overall Threat Level" delay={0.1} />
        </div>

        {/* Prediction Card */}
        <div className="flex-1">
          <GlassCard className="p-8 h-full" delay={0.15}>
            <div className="flex items-start gap-4 mb-6">
              <div className={`p-3 rounded-lg flex-shrink-0 ${isPhishing ? 'bg-red-500/20' : 'bg-green-500/20'}`}>
                {isPhishing ? (
                  <AlertCircle className="w-6 h-6 text-red-400" />
                ) : (
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                )}
              </div>
              <div>
                <h2 className={`text-2xl font-display font-bold mb-2 ${isPhishing ? 'text-red-400' : 'text-green-400'}`}>
                  {isPhishing ? 'PHISHING DETECTED' : 'CLEAN EMAIL PROFILE'}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {isPhishing 
                    ? 'This email shows multiple phishing indicators and should be treated as a threat.'
                    : 'This email appears safe and aligns with legitimate communications patterns.'
                  }
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Confidence</p>
                  <p className="text-2xl font-display font-bold gradient-text">{result.confidence}%</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground mb-1">Detection Severity</p>
                  <p className={`text-sm font-semibold ${isPhishing ? 'text-red-400' : 'text-green-400'}`}>
                    {result.severity}
                  </p>
                </div>
              </div>

              <div className="pt-4 border-t border-white/10">
                <StatusChip 
                  status={isPhishing ? 'danger' : 'success'} 
                  label={isPhishing ? 'Immediate Action Required' : 'Scan Footprints Normal'} 
                />
              </div>
            </div>
          </GlassCard>
        </div>
      </motion.div>

      {/* Threat Indicators */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-6">Threat Indicators</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.indicators.map((indicator, idx) => {
              const Icon = getIconForIndicator(indicator)
              return (
                <ThreatBadge
                  key={idx}
                  icon={Icon}
                  title={indicator}
                  severity={isPhishing ? (result.severity === 'Critical' ? 'critical' : 'high') : 'medium'}
                  delay={0.25 + idx * 0.05}
                />
              )
            })}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.55 }}
            className={`mt-6 p-4 rounded-lg border ${
              isPhishing 
                ? 'bg-yellow-500/10 border-yellow-500/50 text-yellow-200' 
                : 'bg-green-500/10 border-green-500/50 text-green-200'
            }`}
          >
            <p className="text-sm">
              <strong>Recommendation:</strong>{' '}
              {isPhishing 
                ? 'Do not click any links or provide personal information. Report this email to your IT security team immediately.'
                : 'Email is structurally safe. Standard email inspection policies still apply.'
              }
            </p>
          </motion.div>
        </GlassCard>
      </motion.div>

      {/* Email Highlighter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <GlassCard className="p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-display font-bold">Email Highlighted Highlights</h2>
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleCopy}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-sm font-semibold"
              >
                <Copy className="w-4 h-4" />
                Copy Raw
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleDownloadReportText}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-colors text-sm font-semibold"
              >
                <Download className="w-4 h-4" />
                Download Report Text
              </motion.button>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#050811] border border-white/10 overflow-x-auto">
            <pre 
              className="text-xs font-mono text-muted-foreground whitespace-pre-wrap break-words"
              dangerouslySetInnerHTML={{ __html: result.highlighted_email }}
            />
          </div>
        </GlassCard>
      </motion.div>

      {/* Actions */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <motion.button
          onClick={handleDownloadPdf}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          className="p-6 rounded-lg bg-gradient-cyan-purple/10 border border-cyan-500/50 text-center hover:bg-cyan-500/20 hover:shadow-lg hover:shadow-cyan-500/20 transition-all duration-300"
        >
          <Share2 className="w-6 h-6 mx-auto mb-2 text-cyan-400" />
          <p className="font-semibold text-sm">Download PDF Report</p>
        </motion.button>

        <Link href="/dashboard/email-scanner">
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="w-full p-6 rounded-lg bg-gradient-cyan-purple/10 border border-purple-500/50 text-center hover:bg-purple-500/20 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300"
          >
            <Mail className="w-6 h-6 mx-auto mb-2 text-purple-400" />
            <p className="font-semibold text-sm">Analyze Another</p>
          </motion.button>
        </Link>

        <motion.button
          onClick={handleDownloadPdf}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          className="p-6 rounded-lg bg-gradient-cyan-purple/10 border border-pink-500/50 text-center hover:bg-pink-500/20 hover:shadow-lg hover:shadow-pink-500/20 transition-all duration-300"
        >
          <Download className="w-6 h-6 mx-auto mb-2 text-pink-400" />
          <p className="font-semibold text-sm">Get Full PDF Report</p>
        </motion.button>
      </motion.div>
    </motion.div>
  )
}

import { Loader2 } from 'lucide-react'
