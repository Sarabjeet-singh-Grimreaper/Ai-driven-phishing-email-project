'use client'

import { motion } from 'framer-motion'
import { Shield, BookOpen, GitBranch, Terminal, Layers, BarChart2, Cpu, CheckCircle } from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'

export default function AboutPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl md:text-4xl font-display font-bold gradient-text mb-2">
          Project Portfolio & Documentation
        </h1>
        <p className="text-muted-foreground">
          AI CyberShield — Enterprise-grade Email Threat Intelligence Platform (Technical Deep Dive)
        </p>
      </div>

      {/* Overview / Problem Statement */}
      <GlassCard className="p-8">
        <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
          <Shield className="w-5 h-5" /> Problem Statement
        </h2>
        <p className="text-muted-foreground leading-relaxed text-sm">
          Phishing remains the primary vector for enterprise security compromises, accounting for over 90% of data breaches. Modern spear-phishing attacks utilize highly personalized, brand-spoofed, and multi-factor-bypass techniques that evade traditional rule-based gateway secure filters.
        </p>
        <p className="text-muted-foreground leading-relaxed text-sm mt-3">
          **AI CyberShield** addresses this problem by utilizing a hybrid machine learning architecture that blends natural language understanding (NLP) with deep heuristic scanners (evaluating headers, domain similarity, and URL obfuscations) to predict threat levels in real-time, providing explanation metrics for SOC analysts.
        </p>
      </GlassCard>

      {/* Technical Architecture */}
      <GlassCard className="p-8">
        <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
          <Layers className="w-5 h-5" /> Production Architecture
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm mb-6">
          <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
            <h3 className="font-semibold mb-2 text-cyan-300">1. Ingestion & Gateways</h3>
            <p className="text-xs text-muted-foreground">
              Accepts raw email payloads or OCR screenshots. Fast API gateways route requests to microservices synchronously.
            </p>
          </div>
          <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
            <h3 className="font-semibold mb-2 text-purple-300">2. Processing & Calibration</h3>
            <p className="text-xs text-muted-foreground">
              Extracts 28 customized features (SPF check, entropy score, readability indices) and vectorizes bodies via TF-IDF before calibration scaling.
            </p>
          </div>
          <div className="p-4 bg-white/5 border border-white/10 rounded-lg">
            <h3 className="font-semibold mb-2 text-green-300">3. Classifiers & Analytics</h3>
            <p className="text-xs text-muted-foreground">
              Evaluates vectors against random forest classifiers, maps findings to MITRE ATT&CK techniques, and generates ReportLab PDF logs.
            </p>
          </div>
        </div>
      </GlassCard>

      {/* Dataset & Training Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
            <Terminal className="w-5 h-5" /> Training & Preprocessing Pipeline
          </h2>
          <ul className="space-y-3 text-xs text-muted-foreground">
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
              <span>**Real-world Dataset:** 18,650 annotated samples (Phishing_Email.csv) mapped to binary threat labels.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
              <span>**Text Vectorization:** TF-IDF with 4,000 max features and customized English stopwords filtering.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
              <span>**Calibration Steps:** CalibratedClassifierCV ensures predicted probability aligns directly with actual threat likelihood.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
              <span>**Pipeline Integrity:** Complete scikit-learn models saved with version control to prevent feature drift.</span>
            </li>
          </ul>
        </GlassCard>

        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
            <BarChart2 className="w-5 h-5" /> Model Benchmarks
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-muted-foreground space-y-2">
              <thead>
                <tr className="border-b border-white/10 text-cyan-400">
                  <th className="pb-2">Model Class</th>
                  <th className="pb-2">Accuracy</th>
                  <th className="pb-2">Recall</th>
                  <th className="pb-2">Latency</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-white/5">
                  <td className="py-2 text-white font-semibold">Random Forest (Tuned)</td>
                  <td className="py-2">98.1%</td>
                  <td className="py-2">98.7%</td>
                  <td className="py-2">98ms</td>
                </tr>
                <tr className="border-b border-white/5">
                  <td className="py-2">Neural Network (MLP)</td>
                  <td className="py-2">97.5%</td>
                  <td className="py-2">98.0%</td>
                  <td className="py-2">165ms</td>
                </tr>
                <tr className="border-b border-white/5">
                  <td className="py-2">Logistic Regression</td>
                  <td className="py-2">96.8%</td>
                  <td className="py-2">97.4%</td>
                  <td className="py-2">45ms</td>
                </tr>
                <tr>
                  <td className="py-2">Naive Bayes</td>
                  <td className="py-2">94.2%</td>
                  <td className="py-2">95.2%</td>
                  <td className="py-2">22ms</td>
                </tr>
              </tbody>
            </table>
          </div>
        </GlassCard>
      </div>

      {/* Future Work & Features */}
      <GlassCard className="p-8">
        <h2 className="text-xl font-display font-bold mb-4 text-cyan-400 flex items-center gap-2">
          <Cpu className="w-5 h-5" /> Roadmap & Future Work
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
          <div>
            <p className="font-semibold text-cyan-300 mb-1">1. LLM Integration</p>
            <p>Utilize lightweight local models (e.g. Gemma 2B) to output human-readable conversational threat summaries.</p>
          </div>
          <div>
            <p className="font-semibold text-purple-300 mb-1">2. Live API Threat Feeds</p>
            <p>Integrate with external dynamic indicators databases like AlienVault or VirusTotal for real-time URL reputation lookup.</p>
          </div>
        </div>
      </GlassCard>

      {/* Portfolio Links */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
        <a 
          href="https://github.com" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="flex items-center gap-2 px-6 py-3 rounded-lg border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 transition-all duration-200 text-sm font-semibold"
        >
          <GitBranch className="w-4 h-4" /> GitHub Repository
        </a>
        <a 
          href="/docs" 
          className="flex items-center gap-2 px-6 py-3 rounded-lg border border-purple-500/50 text-purple-400 hover:bg-purple-500/10 transition-all duration-200 text-sm font-semibold"
        >
          <BookOpen className="w-4 h-4" /> API Documentation
        </a>
      </div>
    </div>
  )
}
