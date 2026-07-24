'use client'

import { motion } from 'framer-motion'
import { Bell, Lock, Palette, Globe, LogOut, Save } from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'

const settingsSections = [
  {
    icon: Palette,
    title: 'Display Settings',
    description: 'Customize your dashboard appearance',
    items: [
      { label: 'Theme', value: 'Dark Mode', type: 'select' },
      { label: 'Accent Color', value: 'Cyan', type: 'select' },
      { label: 'Compact Layout', value: false, type: 'toggle' },
    ],
  },
  {
    icon: Bell,
    title: 'Notifications',
    description: 'Manage how you receive alerts',
    items: [
      { label: 'Critical Threats', value: true, type: 'toggle' },
      { label: 'Weekly Summary', value: true, type: 'toggle' },
      { label: 'Email Notifications', value: true, type: 'toggle' },
      { label: 'Notification Time', value: '09:00 AM', type: 'select' },
    ],
  },
  {
    icon: Lock,
    title: 'Security',
    description: 'Manage account security settings',
    items: [
      { label: 'Two-Factor Authentication', value: true, type: 'toggle' },
      { label: 'Session Timeout', value: '30 minutes', type: 'select' },
      { label: 'Login Alerts', value: true, type: 'toggle' },
    ],
  },
  {
    icon: Globe,
    title: 'API Settings',
    description: 'Manage API access and tokens',
    items: [
      { label: 'API Key', value: 'sk_live_xxx...', type: 'text' },
      { label: 'Rate Limit', value: '1000 req/min', type: 'select' },
      { label: 'Webhook Enabled', value: true, type: 'toggle' },
    ],
  },
]

export default function SettingsPage() {
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
          Settings
        </h1>
        <p className="text-muted-foreground">Manage your preferences and account settings</p>
      </motion.div>

      {/* Settings Sections */}
      {settingsSections.map((section, sectionIdx) => {
        const Icon = section.icon
        return (
          <motion.div
            key={sectionIdx}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 + sectionIdx * 0.1 }}
          >
            <GlassCard className="p-8">
              <div className="flex items-start gap-4 mb-6">
                <div className="p-3 rounded-lg bg-gradient-cyan-purple/10">
                  <Icon className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-xl font-display font-bold">{section.title}</h2>
                  <p className="text-sm text-muted-foreground mt-1">{section.description}</p>
                </div>
              </div>

              <div className="space-y-4 border-t border-white/10 pt-6">
                {section.items.map((item, itemIdx) => (
                  <motion.div
                    key={itemIdx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.15 + sectionIdx * 0.1 + itemIdx * 0.05 }}
                    className="flex items-center justify-between py-3 border-b border-white/5 last:border-b-0"
                  >
                    <span className="font-medium text-sm">{item.label}</span>

                    {item.type === 'toggle' && (
                      <button className={`w-12 h-6 rounded-full transition-colors ${item.value ? 'bg-cyan-500' : 'bg-white/10'}`}>
                        <div
                          className={`w-5 h-5 rounded-full bg-white transition-transform ${item.value ? 'translate-x-6' : 'translate-x-0.5'}`}
                        />
                      </button>
                    )}

                    {item.type === 'select' && (
                      <select
                        defaultValue={item.value as string}
                        className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50 transition-colors"
                      >
                        <option>{item.value}</option>
                      </select>
                    )}

                    {item.type === 'text' && (
                      <input
                        type="text"
                        defaultValue={item.value as string}
                        className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50 transition-colors w-32"
                      />
                    )}
                  </motion.div>
                ))}
              </div>
            </GlassCard>
          </motion.div>
        )
      })}

      {/* Danger Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <GlassCard className="p-8 border-red-500/50">
          <h2 className="text-xl font-display font-bold text-red-400 mb-2">Danger Zone</h2>
          <p className="text-sm text-muted-foreground mb-6">
            These actions are irreversible. Please proceed with caution.
          </p>

          <div className="space-y-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3 rounded-lg border border-yellow-500/50 text-yellow-400 hover:bg-yellow-500/10 transition-colors font-semibold text-sm"
            >
              Export Data
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3 rounded-lg border border-red-500/50 text-red-400 hover:bg-red-500/10 transition-colors font-semibold text-sm flex items-center justify-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-3 rounded-lg border border-red-500/50 text-red-400 hover:bg-red-500/10 transition-colors font-semibold text-sm"
            >
              Delete Account
            </motion.button>
          </div>
        </GlassCard>
      </motion.div>

      {/* Save Changes */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="flex gap-4"
      >
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 py-3 rounded-lg bg-gradient-cyan-purple text-background font-semibold hover:shadow-2xl hover:shadow-cyan-500/40 transition-all duration-300 flex items-center justify-center gap-2"
        >
          <Save className="w-5 h-5" />
          Save Changes
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 py-3 rounded-lg border border-white/10 text-foreground font-semibold hover:bg-white/5 transition-all duration-300"
        >
          Reset
        </motion.button>
      </motion.div>
    </motion.div>
  )
}
