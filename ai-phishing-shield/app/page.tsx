'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Shield,
  ArrowRight,
  GitBranch,
  BookOpen,
  Play,
  Lock,
  Brain,
  Zap,
  Eye,
} from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Detection',
    description: 'Advanced machine learning models detect phishing patterns in milliseconds',
  },
  {
    icon: Lock,
    title: 'Enterprise Security',
    description: 'Bank-grade encryption and security protocols for your data protection',
  },
  {
    icon: Eye,
    title: 'Email Analysis',
    description: 'Deep inspection of email headers, content, and embedded resources',
  },
  {
    icon: Zap,
    title: 'Real-time Results',
    description: 'Instant threat detection and comprehensive risk assessment reporting',
  },
]

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

    const particles: Array<{
      x: number
      y: number
      vx: number
      vy: number
      size: number
      opacity: number
    }> = []

    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.5,
        vy: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.5 + 0.2,
      })
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.fillStyle = 'rgba(6, 182, 212, 0.1)'

      particles.forEach((p) => {
        p.x += p.vx
        p.y += p.vy

        if (p.x < 0) p.x = canvas.width
        if (p.x > canvas.width) p.x = 0
        if (p.y < 0) p.y = canvas.height
        if (p.y > canvas.height) p.y = 0

        ctx.globalAlpha = p.opacity
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2)
        ctx.fill()
      })

      requestAnimationFrame(animate)
    }

    animate()

    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-background via-background to-slate-900 overflow-hidden">
      {/* Animated background canvas */}
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-none opacity-40"
      />

      {/* Animated gradient orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl animate-float" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-float-delayed" />
      </div>

      <div className="relative z-10">
        {/* Navigation */}
        <motion.nav
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between p-6 md:px-12 md:py-8 glass-dark glass-border backdrop-blur-xl border-b"
        >
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-gradient-cyan-purple/20">
              <Shield className="w-6 h-6 text-cyan-400" />
            </div>
            <div className="flex flex-col">
              <span className="font-display font-bold text-lg gradient-text">AI CyberShield</span>
              <span className="text-xs text-muted-foreground leading-none">Threat Intel</span>
            </div>
          </div>

          <Link href="/dashboard">
            <button className="flex items-center gap-2 px-6 py-2 rounded-lg bg-gradient-cyan-purple/20 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/20 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/30 text-sm font-semibold">
              Dashboard
              <ArrowRight className="w-4 h-4" />
            </button>
          </Link>
        </motion.nav>

        {/* Hero Section */}
        <section className="min-h-[90vh] flex flex-col items-center justify-center px-6 md:px-12 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-display font-bold mb-6 gradient-text">
              Detect Phishing Emails
              <br />
              Before They Strike
            </h1>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg md:text-xl text-muted-foreground max-w-2xl mb-8"
          >
            Enterprise-grade AI phishing detection powered by advanced machine learning. Analyze
            emails in real-time and protect your organization from sophisticated threats.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col md:flex-row gap-4 mb-16"
          >
            <Link href="/dashboard/email-scanner">
              <button className="flex items-center justify-center gap-2 px-8 py-4 rounded-lg bg-gradient-cyan-purple text-background font-semibold hover:shadow-2xl hover:shadow-cyan-500/40 transition-all duration-300 transform hover:scale-105">
                Analyze Email
                <ArrowRight className="w-5 h-5" />
              </button>
            </Link>

            <button className="flex items-center justify-center gap-2 px-8 py-4 rounded-lg border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/10 transition-all duration-300">
              <Play className="w-5 h-5" />
              Watch Demo
            </button>
          </motion.div>

          {/* Floating Feature Cards */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mb-12"
          >
            {features.map((feature, idx) => {
              const Icon = feature.icon
              return (
                <GlassCard
                  key={idx}
                  delay={0.4 + idx * 0.1}
                  className="p-6 text-left hover:shadow-lg hover:shadow-cyan-500/20"
                >
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-lg bg-gradient-cyan-purple/10 flex-shrink-0">
                      <Icon className="w-6 h-6 text-cyan-400" />
                    </div>
                    <div>
                      <h3 className="font-display font-bold mb-2">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </div>
                </GlassCard>
              )
            })}
          </motion.div>

          {/* CTA Links */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="flex flex-wrap justify-center gap-6 text-sm"
          >
            <button className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors">
              <GitBranch className="w-4 h-4" />
              View on GitHub
            </button>
            <button className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors">
              <BookOpen className="w-4 h-4" />
              Documentation
            </button>
          </motion.div>
        </section>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1 }}
          className="border-t border-white/10 py-8 px-6 md:px-12 text-center text-sm text-muted-foreground"
        >
          <p>AI CyberShield • Powered by advanced machine learning • v2.0</p>
        </motion.footer>
      </div>
    </div>
  )
}
