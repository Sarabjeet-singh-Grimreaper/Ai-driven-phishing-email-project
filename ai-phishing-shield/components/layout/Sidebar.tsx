'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  BarChart3,
  Brain,
  FileText,
  Home,
  Mail,
  Settings,
  Shield,
  AlertCircle,
  Zap,
  Info,
} from 'lucide-react'
import { GlassCard } from '../cards/GlassCard'
import { motion } from 'framer-motion'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: Home },
  { href: '/dashboard/email-scanner', label: 'Email Scanner', icon: Mail },
  { href: '/dashboard/threat-intelligence', label: 'Threats', icon: AlertCircle },
  { href: '/dashboard/analytics', label: 'Analytics', icon: BarChart3 },
  { href: '/dashboard/models', label: 'Models', icon: Brain },
  { href: '/dashboard/reports', label: 'Reports', icon: FileText },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
  { href: '/dashboard/about', label: 'About', icon: Info },
]

export const Sidebar = () => {
  const pathname = usePathname()

  return (
    <GlassCard className="w-full md:w-64 md:h-screen md:sticky md:top-0 md:rounded-none md:border-r md:border-l-0 md:border-t-0 md:border-b-0 p-0 glass-dark">
      <div className="flex flex-col h-full p-4 md:p-6">
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2 mb-8 px-2"
        >
          <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30 backdrop-blur">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <div className="hidden md:flex flex-col">
            <span className="font-sans font-bold text-lg gradient-text">
              Phishing
            </span>
            <span className="text-xs text-slate-400">Shield</span>
          </div>
        </motion.div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2">
          {navItems.map((item, idx) => {
            const Icon = item.icon
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)

            return (
              <motion.div
                key={item.href}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.05 }}
              >
                <Link href={item.href}>
                  <div
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/30 border border-cyan-500/20'
                        : 'text-slate-400 hover:text-foreground hover:bg-cyan-500/10'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="hidden md:inline text-sm font-medium">{item.label}</span>
                    {isActive && (
                      <div className="ml-auto w-1 h-6 bg-cyan-400 rounded-full" />
                    )}
                  </div>
                </Link>
              </motion.div>
            )
          })}
        </nav>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="pt-4 border-t border-cyan-500/20 hidden md:flex flex-col gap-2 text-xs text-slate-400"
        >
          <p>v1.0 • AI-Powered</p>
          <p>Phishing Detection</p>
        </motion.div>
      </div>
    </GlassCard>
  )
}
