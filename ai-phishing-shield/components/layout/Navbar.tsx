'use client'

import { Search, Bell, Settings } from 'lucide-react'
import { GlassCard } from '../cards/GlassCard'
import { motion } from 'framer-motion'

export const Navbar = () => {
  return (
    <GlassCard className="sticky top-0 z-40 rounded-none border-b border-l-0 border-r-0 border-t-0 md:rounded-none p-4 md:p-6">
      <div className="flex items-center justify-between gap-4">
        {/* Search */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="flex-1 hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 hover:bg-cyan-500/15 transition-colors"
        >
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search..."
            className="flex-1 bg-transparent text-sm outline-none placeholder-slate-500 text-foreground"
          />
        </motion.div>

        {/* Right section */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="flex items-center gap-3"
        >
          {/* Search icon for mobile */}
          <button className="md:hidden p-2 hover:bg-cyan-500/10 rounded-lg transition-colors">
            <Search className="w-5 h-5 text-slate-400" />
          </button>

          {/* Notifications */}
          <button className="relative p-2 hover:bg-cyan-500/10 rounded-lg transition-colors group">
            <Bell className="w-5 h-5 text-slate-400 group-hover:text-cyan-400" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          </button>

          {/* Settings */}
          <button className="p-2 hover:bg-cyan-500/10 rounded-lg transition-colors">
            <Settings className="w-5 h-5 text-slate-400 hover:text-cyan-400" />
          </button>

          {/* Avatar */}
          <div className="hidden md:flex items-center gap-3 pl-3 border-l border-cyan-500/20">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-600 to-blue-600 p-0.5">
              <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center">
                <span className="text-xs font-bold text-cyan-400 font-mono">A</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </GlassCard>
  )
}
