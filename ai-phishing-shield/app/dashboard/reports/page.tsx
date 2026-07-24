'use client'

import { motion } from 'framer-motion'
import {
  FileText,
  Download,
  Calendar,
  Share2,
  MoreHorizontal,
  Plus,
} from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'
import { getReportPdfUrl } from '@/services/api'
import toast from 'react-hot-toast'

const reports = [
  {
    id: 'monthly-1',
    name: 'Monthly Security Report',
    date: 'Jan 2024',
    type: 'Monthly',
    scans: 24582,
    threats: 342,
    accuracy: 98.1,
  },
  {
    id: 'weekly-1',
    name: 'Weekly Threat Summary',
    date: 'Week of Jan 15',
    type: 'Weekly',
    scans: 3420,
    threats: 45,
    accuracy: 98.3,
  },
  {
    id: 'exec-1',
    name: 'Executive Dashboard',
    date: 'Jan 2024',
    type: 'Executive',
    scans: 24582,
    threats: 342,
    accuracy: 98.1,
  },
  {
    id: 'compliance-1',
    name: 'Compliance Report',
    date: 'Q4 2023',
    type: 'Quarterly',
    scans: 75200,
    threats: 1020,
    accuracy: 98.2,
  },
]

export default function ReportsPage() {
  const handleDownload = (id: string) => {
    const url = getReportPdfUrl(id)
    window.open(url, '_blank')
    toast.success('Initiating PDF summary download...')
  }

  const handleShare = () => {
    toast.success('Share link copied to clipboard.')
  }

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
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl md:text-4xl font-display font-bold gradient-text mb-2">
            Reports
          </h1>
          <p className="text-muted-foreground">Generate and manage threat detection reports</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="hidden md:flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-cyan-purple text-background font-semibold"
        >
          <Plus className="w-5 h-5" />
          New Report
        </motion.button>
      </motion.div>

      {/* Reports List */}
      <motion.div
        className="space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        {reports.map((report, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.15 + idx * 0.05 }}
          >
            <GlassCard 
              className="p-6 hover:shadow-lg hover:shadow-cyan-500/20 cursor-pointer"
              onClick={() => handleDownload(report.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className="p-3 rounded-lg bg-gradient-cyan-purple/10 flex-shrink-0">
                    <FileText className="w-6 h-6 text-cyan-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold mb-1">{report.name}</h3>
                    <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {report.date}
                      </span>
                      <span>Type: {report.type}</span>
                      <span>{report.scans.toLocaleString()} scans</span>
                      <span className="text-red-400">{report.threats} threats</span>
                      <span className="text-green-400">{report.accuracy}% accuracy</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4" onClick={(e) => e.stopPropagation()}>
                  <motion.button
                    onClick={() => handleDownload(report.id)}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <Download className="w-5 h-5 text-cyan-400" />
                  </motion.button>
                  <motion.button
                    onClick={handleShare}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <Share2 className="w-5 h-5 text-purple-400" />
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <MoreHorizontal className="w-5 h-5 text-muted-foreground" />
                  </motion.button>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </motion.div>

      {/* Report Builder */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.35 }}
      >
        <GlassCard className="p-8">
          <h2 className="text-xl font-display font-bold mb-6">Generate Custom Report</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-semibold mb-2">Report Type</label>
              <select className="w-full p-3 rounded-lg bg-white/5 border border-white/10 text-foreground focus:outline-none focus:border-cyan-500/50 transition-colors">
                <option>Monthly Summary</option>
                <option>Weekly Threat Report</option>
                <option>Executive Dashboard</option>
                <option>Compliance Report</option>
                <option>Custom Range</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Date Range</label>
              <input
                type="date"
                className="w-full p-3 rounded-lg bg-white/5 border border-white/10 text-foreground focus:outline-none focus:border-cyan-500/50 transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Include Metrics</label>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" defaultChecked className="w-4 h-4 rounded" />
                  Detection Rate
                </label>
                <label className="flex items-center gap-2 text-sm cursor-pointer">
                  <input type="checkbox" defaultChecked className="w-4 h-4 rounded" />
                  Threat Distribution
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2">Output Format</label>
              <select className="w-full p-3 rounded-lg bg-white/5 border border-white/10 text-foreground focus:outline-none focus:border-cyan-500/50 transition-colors">
                <option>PDF</option>
                <option>CSV</option>
                <option>JSON</option>
                <option>Email</option>
              </select>
            </div>
          </div>

          <motion.button
            onClick={() => handleDownload('custom')}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="w-full py-3 rounded-lg bg-gradient-cyan-purple text-background font-semibold hover:shadow-2xl hover:shadow-cyan-500/40 transition-all duration-300"
          >
            Generate Report
          </motion.button>
        </GlassCard>
      </motion.div>
    </motion.div>
  )
}
