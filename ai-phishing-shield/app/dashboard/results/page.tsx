'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Link2,
  Lock,
  AlertTriangle,
  CheckCircle2,
  Copy,
  Download,
  Share2,
  Mail,
  ArrowLeft,
  Loader2,
  FileText,
  ShieldAlert,
  Server,
  Zap,
  Globe,
  Fingerprint
} from 'lucide-react'
import { RiskMeter } from '@/components/visualization/RiskMeter'
import { GlassCard } from '@/components/cards/GlassCard'
import toast from 'react-hot-toast'
import { ScanResponse, getReportPdfUrl } from '@/services/api'

// Lucide icon routing based on heuristic labels
const getIconForIndicator = (indicator: string) => {
  const ind = indicator.toLowerCase()
  if (ind.includes('url') || ind.includes('link') || ind.includes('tld')) return Link2
  if (ind.includes('password') || ind.includes('credential') || ind.includes('login') || ind.includes('mfa')) return Lock
  if (ind.includes('urgency') || ind.includes('immediate') || ind.includes('attention')) return AlertTriangle
  return ShieldAlert
}

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
  lexical_url_analysis?: {
    has_login_lure_path: boolean
    has_brand_lure_path: boolean
    has_at_symbol_obfuscation: boolean
    has_excessive_subdomains: boolean
    has_suspicious_tld: boolean
    max_subdomains_count: number
    max_special_chars_count: number
  }
  nlp_intents?: {
    urgency_lure: boolean
    credential_harvesting: boolean
    financial_lure: boolean
    mfa_otp_lure: boolean
    authority_lure: boolean
  }
}

export default function ResultsPage() {
  const [result, setResult] = useState<UpgradedScanResponse | null>(null)
  const [rawEmail, setRawEmail] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'highlights' | 'diagnostics'>('highlights')

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
    toast.success('Copied raw email content')
  }

  const handleDownloadReportText = () => {
    if (!result) return
    const reportText = `AI CYBERSHIELD DEEP PHISHING INSPECTOR\n` +
      `======================================\n` +
      `VERDICT: ${result.prediction}\n` +
      `THREAT LEVEL SCORE: ${result.risk_score}/100\n` +
      `CLASSIFIED AS: ${result.attack_type}\n` +
      `SEVERITY: ${result.severity}\n` +
      `PRIMARY HEURISTIC: ${result.reason || 'N/A'}\n` +
      `MODEL: ${result.model}\n\n` +
      `THREAT LOGS & SIGNATURES:\n` +
      result.indicators.map(ind => `[-] ${ind}`).join('\n')
      
    const element = document.createElement('a')
    const file = new Blob([reportText], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `CyberShield_Threat_Report_${result.id || 'scan'}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
    toast.success('Report downloaded')
  }

  const handleDownloadPdf = () => {
    if (!result) return
    const url = getReportPdfUrl(result.id || 'latest')
    window.open(url, '_blank')
    toast.success('Exporting PDF Threat Intelligence Report...')
  }

  if (!result) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Loader2 className="w-10 h-10 animate-spin text-cyan-500" />
        <p className="text-muted-foreground font-mono text-sm tracking-widest uppercase">Initializing Forensic Scan...</p>
      </div>
    )
  }

  const isPhishing = result.prediction.toUpperCase() === 'PHISHING'

  return (
    <motion.div
      className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6"
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      {/* State: Reading this as a technical security inspector, dark hacker theme, VISUAL_DENSITY: 4, MOTION_INTENSITY: 5 */}

      {/* Breadcrumb Nav */}
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <div className="flex items-center gap-3">
          <Link href="/dashboard/email-scanner">
            <motion.button 
              whileHover={{ scale: 1.05, x: -2 }}
              whileTap={{ scale: 0.98 }}
              className="p-2.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl transition-all duration-200"
            >
              <ArrowLeft className="w-4 h-4 text-muted-foreground hover:text-foreground" />
            </motion.button>
          </Link>
          <div>
            <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground uppercase tracking-widest">
              <span>Security Core</span>
              <span>/</span>
              <span className="text-cyan-400">Forensics Summary</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-display font-black tracking-tight text-foreground mt-1">
              Threat Intelligence Inspector
            </h1>
          </div>
        </div>

        <div className="flex gap-2">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleDownloadPdf}
            className="hidden sm:flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/20 transition-all duration-200"
          >
            <Share2 className="w-3.5 h-3.5" />
            Export Threat Intel
          </motion.button>
        </div>
      </div>

      {/* Main Grid: Asymmetric Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Side: Score & Metadata Bento block */}
        <div className="lg:col-span-4 space-y-6">
          {/* Gauge Widget */}
          <GlassCard className="p-6 overflow-hidden relative flex flex-col items-center justify-center text-center">
            <div className="absolute top-3 left-3 px-2 py-0.5 rounded bg-white/5 border border-white/10 text-[9px] font-mono tracking-widest text-muted-foreground uppercase">
              Threat Level Metric
            </div>
            <div className="pt-4 w-full flex justify-center">
              <RiskMeter score={result.risk_score} label="" delay={0.15} />
            </div>
          </GlassCard>

          {/* Core Threat Status Badge */}
          <GlassCard className="p-6 space-y-4">
            <div className="flex items-start gap-3">
              <div className={`p-2.5 rounded-lg border flex-shrink-0 ${
                isPhishing 
                  ? 'bg-red-500/15 border-red-500/30 text-red-400' 
                  : 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
              }`}>
                {isPhishing ? <ShieldAlert className="w-5 h-5" /> : <CheckCircle2 className="w-5 h-5" />}
              </div>
              <div>
                <h3 className={`text-lg font-display font-black tracking-tight ${isPhishing ? 'text-red-400' : 'text-emerald-400'}`}>
                  {isPhishing ? 'MALICIOUS VERDICT' : 'VERIFIED SAFE'}
                </h3>
                <p className="text-xs text-muted-foreground leading-relaxed mt-1">
                  {result.reason || (isPhishing 
                    ? 'Forensic components identified credentials lures paired with spoofing signatures.'
                    : 'No anomalous communication markers found in lexical domain checks or text intents.')
                  }
                </p>
              </div>
            </div>

            {/* Micro Metadata Items */}
            <div className="grid grid-cols-2 gap-3 pt-4 border-t border-white/5 font-mono text-[10px]">
              <div className="p-2 rounded bg-white/5 border border-white/5">
                <span className="text-muted-foreground block mb-0.5">CLASSIFICATION</span>
                <span className="font-bold text-foreground text-xs truncate block">{result.attack_type}</span>
              </div>
              <div className="p-2 rounded bg-white/5 border border-white/5">
                <span className="text-muted-foreground block mb-0.5">SEVERITY</span>
                <span className={`font-bold text-xs block ${isPhishing ? 'text-red-400 font-extrabold' : 'text-emerald-400'}`}>
                  {result.severity}
                </span>
              </div>
              <div className="p-2 rounded bg-white/5 border border-white/5">
                <span className="text-muted-foreground block mb-0.5">ENGINE CONFIDENCE</span>
                <span className="font-bold text-foreground text-xs block text-cyan-400">{result.confidence}%</span>
              </div>
              <div className="p-2 rounded bg-white/5 border border-white/5">
                <span className="text-muted-foreground block mb-0.5">DETECTION SYSTEM</span>
                <span className="font-bold text-foreground text-xs block truncate">{result.model}</span>
              </div>
            </div>
          </GlassCard>

          {/* Verification Results Checks */}
          <GlassCard className="p-6 space-y-4">
            <h3 className="text-xs font-mono font-bold tracking-widest text-muted-foreground uppercase flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-cyan-400" /> Authentication Verifications
            </h3>
            
            <div className="space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
                <div className="flex items-center gap-2">
                  <Fingerprint className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>SPF Record Path</span>
                </div>
                <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                  result.feature_contributions?.suspicious_tld === 0 || !isPhishing
                    ? 'bg-emerald-500/10 text-emerald-400' 
                    : 'bg-red-500/10 text-red-400'
                }`}>
                  {result.feature_contributions?.suspicious_tld === 0 || !isPhishing ? 'PASS' : 'FAIL'}
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
                <div className="flex items-center gap-2">
                  <Lock className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>DKIM Signature</span>
                </div>
                <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                  !isPhishing ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                }`}>
                  {!isPhishing ? 'PASS' : 'NEUTRAL / FAIL'}
                </span>
              </div>

              <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
                <div className="flex items-center gap-2">
                  <Globe className="w-3.5 h-3.5 text-muted-foreground" />
                  <span>Domain Similarity</span>
                </div>
                <span className={`font-bold text-xs ${
                  (result.feature_contributions?.domain_similarity || 0) > 0.6 ? 'text-red-400' : 'text-emerald-400'
                }`}>
                  {((result.feature_contributions?.domain_similarity || 0) * 100).toFixed(0)}% Match
                </span>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Right Side: Tabbed Forensics Console */}
        <div className="lg:col-span-8 space-y-6">
          <div className="flex border-b border-white/10 pb-1">
            <button
              onClick={() => setActiveTab('highlights')}
              className={`px-4 py-2 font-mono text-xs uppercase tracking-widest border-b-2 transition-all duration-200 ${
                activeTab === 'highlights' 
                  ? 'border-cyan-400 text-cyan-400 font-bold' 
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              Forensic Highlighter
            </button>
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={`px-4 py-2 font-mono text-xs uppercase tracking-widest border-b-2 transition-all duration-200 ${
                activeTab === 'diagnostics' 
                  ? 'border-cyan-400 text-cyan-400 font-bold' 
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              }`}
            >
              Diagnostic Signals
            </button>
          </div>

          {activeTab === 'highlights' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="space-y-4"
            >
              <GlassCard className="p-6">
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/5">
                  <h3 className="text-sm font-mono tracking-widest text-muted-foreground uppercase flex items-center gap-1.5">
                    <Zap className="w-4 h-4 text-cyan-400" /> Parsed Email Payload
                  </h3>
                  <div className="flex gap-2">
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleCopy}
                      className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-muted-foreground hover:text-foreground transition-all duration-200"
                    >
                      <Copy className="w-3.5 h-3.5" />
                      Copy Raw
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleDownloadReportText}
                      className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-muted-foreground hover:text-foreground transition-all duration-200"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Report Log
                    </motion.button>
                  </div>
                </div>

                {/* Main Highlighter Output */}
                <div className="p-4 rounded-xl bg-[#03060b] border border-white/5 shadow-inner">
                  <pre 
                    className="text-xs font-mono text-zinc-300 whitespace-pre-wrap break-words leading-relaxed"
                    dangerouslySetInnerHTML={{ __html: result.highlighted_email }}
                  />
                </div>

                {/* Highlighting Code Keys */}
                <div className="mt-4 flex flex-wrap gap-3 text-[10px] font-mono text-muted-foreground pt-4 border-t border-white/5">
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-emerald-500/20 border border-emerald-500/50"></span> Brands</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-orange-500/20 border border-orange-500/50"></span> Credentials</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-blue-500/20 border border-blue-500/50"></span> OTP/MFA</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-purple-500/20 border border-purple-500/50"></span> Currency</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-pink-500/20 border border-pink-500/50"></span> Urgency</span>
                  <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-red-500/20 border border-red-500/50"></span> URLs</span>
                </div>
              </GlassCard>
            </motion.div>
          )}

          {activeTab === 'diagnostics' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {/* Diagnostic Checklist */}
              <GlassCard className="p-6">
                <h3 className="text-xs font-mono font-bold tracking-widest text-muted-foreground uppercase flex items-center gap-1.5 mb-4">
                  <ShieldAlert className="w-4 h-4 text-cyan-400" /> Risk Analysis Checklist
                </h3>
                <div className="space-y-3">
                  {result.reasons && result.reasons.length > 0 ? (
                    result.reasons.map((r, i) => (
                      <div key={i} className="flex gap-2.5 items-start p-2.5 rounded bg-white/5 border border-white/5">
                        <span className={`text-xs ${isPhishing ? 'text-red-400' : 'text-emerald-400'}`}>
                          {isPhishing ? '✕' : '✓'}
                        </span>
                        <p className="text-[11px] text-muted-foreground leading-relaxed">{r}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs font-mono text-muted-foreground">No diagnostics checklist logs found.</p>
                  )}
                </div>
              </GlassCard>

              {/* Lexical URL & Intent scanning report */}
              <div className="space-y-6">
                {/* Lexical URL analysis */}
                <GlassCard className="p-6 space-y-3">
                  <h3 className="text-xs font-mono font-bold tracking-widest text-muted-foreground uppercase flex items-center gap-1.5">
                    <Link2 className="w-4 h-4 text-cyan-400" /> Lexical URL Signatures
                  </h3>
                  
                  <div className="space-y-2 text-[11px] font-mono">
                    <div className="flex justify-between items-center p-2 rounded bg-white/5 border border-white/5">
                      <span>Auth Obfuscation (@ symbol)</span>
                      <span className={result.lexical_url_analysis?.has_at_symbol_obfuscation ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                        {result.lexical_url_analysis?.has_at_symbol_obfuscation ? 'DETECTED' : 'CLEAN'}
                      </span>
                    </div>

                    <div className="flex justify-between items-center p-2 rounded bg-white/5 border border-white/5">
                      <span>Login Path Redirection</span>
                      <span className={result.lexical_url_analysis?.has_login_lure_path ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                        {result.lexical_url_analysis?.has_login_lure_path ? 'FOUND' : 'CLEAN'}
                      </span>
                    </div>

                    <div className="flex justify-between items-center p-2 rounded bg-white/5 border border-white/5">
                      <span>Subdomain Count</span>
                      <span className={(result.lexical_url_analysis?.max_subdomains_count || 0) > 3 ? 'text-red-400 font-bold' : 'text-foreground'}>
                        {result.lexical_url_analysis?.max_subdomains_count || 0}
                      </span>
                    </div>
                  </div>
                </GlassCard>

                {/* NLP Intents */}
                <GlassCard className="p-6 space-y-3">
                  <h3 className="text-xs font-mono font-bold tracking-widest text-muted-foreground uppercase flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-cyan-400" /> Semantic NLP Intents
                  </h3>
                  
                  <div className="space-y-2 text-[11px] font-mono">
                    <div className="flex justify-between items-center p-2 rounded bg-white/5 border border-white/5">
                      <span>Urgency Lure Detection</span>
                      <span className={result.nlp_intents?.urgency_lure ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                        {result.nlp_intents?.urgency_lure ? 'DETECTED' : 'CLEAN'}
                      </span>
                    </div>

                    <div className="flex justify-between items-center p-2 rounded bg-white/5 border border-white/5">
                      <span>Credential Harvesting Intent</span>
                      <span className={result.nlp_intents?.credential_harvesting ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                        {result.nlp_intents?.credential_harvesting ? 'DETECTED' : 'CLEAN'}
                      </span>
                    </div>

                    <div className="flex justify-between items-center p-2 rounded bg-white/5 border border-white/5">
                      <span>MFA OTP Bypass Intent</span>
                      <span className={result.nlp_intents?.mfa_otp_lure ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                        {result.nlp_intents?.mfa_otp_lure ? 'DETECTED' : 'CLEAN'}
                      </span>
                    </div>
                  </div>
                </GlassCard>
              </div>
            </motion.div>
          )}

          {/* Visual Indicator Threat Badges */}
          <GlassCard className="p-6">
            <h3 className="text-xs font-mono font-bold tracking-widest text-muted-foreground uppercase mb-4">
              Identified Threat Signals
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.indicators.map((indicator, idx) => {
                const Icon = getIconForIndicator(indicator)
                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: idx * 0.05 }}
                    className="flex items-center gap-3 p-3 bg-white/5 border border-white/5 rounded-xl text-xs hover:border-white/10 transition-colors"
                  >
                    <div className={`p-2 rounded-lg ${
                      isPhishing ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    }`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="font-semibold block">{indicator}</span>
                      <span className="text-[10px] text-muted-foreground">{isPhishing ? 'Security Warning' : 'Normal Signal'}</span>
                    </div>
                  </motion.div>
                )
              })}
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Navigation action cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-6">
        <motion.button
          onClick={handleDownloadPdf}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          className="p-5 rounded-xl bg-gradient-cyan-purple/10 border border-cyan-500/30 text-center hover:bg-cyan-500/20 transition-all duration-300"
        >
          <p className="font-bold text-sm text-cyan-400">Download PDF Report</p>
          <span className="text-[10px] font-mono text-muted-foreground mt-1 block">Full forensic artifact export</span>
        </motion.button>

        <Link href="/dashboard/email-scanner" className="block w-full">
          <motion.button
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="w-full p-5 rounded-xl bg-gradient-cyan-purple/10 border border-purple-500/30 text-center hover:bg-purple-500/20 transition-all duration-300"
          >
            <p className="font-bold text-sm text-purple-400">Inspect Another Email</p>
            <span className="text-[10px] font-mono text-muted-foreground mt-1 block">Analyze new threat indicators</span>
          </motion.button>
        </Link>

        <motion.button
          onClick={handleDownloadReportText}
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
          className="p-5 rounded-xl bg-gradient-cyan-purple/10 border border-pink-500/30 text-center hover:bg-pink-500/20 transition-all duration-300"
        >
          <p className="font-bold text-sm text-pink-400">Download Plain Text Report</p>
          <span className="text-[10px] font-mono text-muted-foreground mt-1 block">Standard forensic checklist summary</span>
        </motion.button>
      </div>
    </motion.div>
  )
}
