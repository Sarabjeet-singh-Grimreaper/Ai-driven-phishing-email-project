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
  Loader2,
  FileText,
  BarChart,
  Cpu
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

// Extends API ScanResponse definition locally to include explainability upgrades
interface UpgradedScanResponse extends ScanResponse {
  reason?: string
  reasons?: string[]
  feature_contributions?: {
    url_count: number
    suspicious_tld: number
    urgency_score: number
    sentiment_score: number
    entropy_score: number
    domain_similarity: number
    brand_detected: number
    brand_name: string
    money_keywords: number
    otp_keywords: number
    password_keywords: number
  }
}

export default function ResultsPage() {
  const [result, setResult] = useState<UpgradedScanResponse | null>(null)
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
      `Primary Reason: ${result.reason || 'N/A'}\n` +
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
    if (!result) return
    const url = getReportPdfUrl(result.id || 'latest')
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

  const isPhishing = result.prediction.toUpperCase() === 'PHISHING'

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
        <div className="flex-1 flex justify-center w-full md:w-auto">
          <RiskMeter score={result.risk_score} label="Overall Threat Level" delay={0.1} />
        </div>

        {/* Prediction Card */}
        <div className="flex-1 w-full">
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
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {result.reason || (isPhishing 
                    ? 'This email shows multiple phishing indicators and should be treated as a threat.'
                    : 'This email appears safe and aligns with legitimate communications patterns.')
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
                  <p className={`text-sm font-bold ${isPhishing ? 'text-red-400' : 'text-green-400'}`}>
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

      {/* Explainable AI: Reasons & Contributors */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Indicators checklist */}
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
            <Cpu className="w-5 h-5" /> Threat Explanation Checklist
          </h2>
          <p className="text-xs text-muted-foreground mb-4">
            {isPhishing 
              ? 'Below are the risk signals discovered during structural heuristics and semantic parsing:' 
              : 'Below are the positive indicators validating the legitimacy of this communication:'
            }
          </p>

          <div className="space-y-3">
            {result.reasons && result.reasons.length > 0 ? (
              result.reasons.map((r, i) => (
                <div key={i} className="flex items-start gap-3 p-3 bg-white/5 border border-white/10 rounded-lg text-xs">
                  <span className={`font-bold ${isPhishing ? 'text-red-400' : 'text-green-400'}`}>
                    {isPhishing ? '⚠️' : '✓'}
                  </span>
                  <p className="text-muted-foreground leading-relaxed">{r}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground">No specific diagnostic logs compiled.</p>
            )}
          </div>
        </GlassCard>

        {/* Feature Contribution Panel */}
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
            <BarChart className="w-5 h-5" /> Feature Contribution Analysis
          </h2>
          <p className="text-xs text-muted-foreground mb-4">
            Extracted heuristic values processed by the calibrated Random Forest classification engine:
          </p>

          {result.feature_contributions ? (
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">URL Count</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.url_count}</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">Suspicious TLD</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.suspicious_tld > 0 ? 'Yes (ru/xyz/zip)' : 'No'}</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">Urgency Score</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.urgency_score} keywords</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">Sentiment Score</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.sentiment_score} index</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">URL Entropy</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.entropy_score} bits</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">Domain Similarity</span>
                <span className="font-bold text-sm text-cyan-400">{(result.feature_contributions.domain_similarity * 100).toFixed(1)}%</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">Brand Impersonation</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.brand_name}</span>
              </div>
              <div className="p-3 bg-white/5 border border-white/5 rounded-lg">
                <span className="text-muted-foreground block mb-1">Password Keywords</span>
                <span className="font-bold text-sm text-cyan-400">{result.feature_contributions.password_keywords} triggers</span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground">Feature values mapping unavailable.</p>
          )}
        </GlassCard>
      </motion.div>

      {/* Threat Indicators Badge List */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-6">Threat Signatures</h2>
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
        </GlassCard>
      </motion.div>

      {/* Email Highlighter */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.35 }}
      >
        <GlassCard className="p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-display font-bold">Heuristic Segment Highlighting</h2>
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
          
          {/* Color Key Guide */}
          <div className="mt-4 flex flex-wrap gap-4 text-[10px] text-muted-foreground border-t border-white/5 pt-4">
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-cyan-400/20 border border-cyan-400/50"></span> Brands</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-orange-400/20 border border-orange-400/50"></span> Credentials</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-blue-400/20 border border-blue-400/50"></span> OTP/MFA</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-purple-400/20 border border-purple-400/50"></span> Currency</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-pink-400/20 border border-pink-400/50"></span> Urgency</span>
            <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-red-400/20 border border-red-400/50"></span> URLs</span>
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
          <p className="font-semibold text-sm">Download PDF Threat Report</p>
        </motion.button>

        <Link href="/dashboard/email-scanner" className="block w-full">
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="w-full p-6 rounded-lg bg-gradient-cyan-purple/10 border border-purple-500/50 text-center hover:bg-purple-500/20 hover:shadow-lg hover:shadow-purple-500/20 transition-all duration-300"
          >
            <Mail className="w-6 h-6 mx-auto mb-2 text-purple-400" />
            <p className="font-semibold text-sm">Analyze Another Email</p>
          </motion.button>
        </Link>

        <motion.button
          onClick={handleDownloadPdf}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          className="w-full p-6 rounded-lg bg-gradient-cyan-purple/10 border border-pink-500/50 text-center hover:bg-pink-500/20 hover:shadow-lg hover:shadow-pink-500/20 transition-all duration-300"
        >
          <FileText className="w-6 h-6 mx-auto mb-2 text-pink-400" />
          <p className="font-semibold text-sm">Get Dynamic Executive Report</p>
        </motion.button>
      </motion.div>
    </motion.div>
  )
}
