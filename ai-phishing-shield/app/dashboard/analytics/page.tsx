'use client'

import { motion } from 'framer-motion'
import { GlassCard } from '@/components/cards/GlassCard'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

const scanTrendData = [
  { date: 'Mon', scans: 4200, threats: 240 },
  { date: 'Tue', scans: 3800, threats: 221 },
  { date: 'Wed', scans: 5100, threats: 280 },
  { date: 'Thu', scans: 4900, threats: 260 },
  { date: 'Fri', scans: 6200, threats: 340 },
  { date: 'Sat', scans: 5800, threats: 310 },
  { date: 'Sun', scans: 4600, threats: 200 },
]

const threatDistribution = [
  { name: 'Phishing', value: 45 },
  { name: 'Malware', value: 25 },
  { name: 'Spoofing', value: 20 },
  { name: 'Other', value: 10 },
]

const accuracyData = [
  { month: 'Jan', accuracy: 96.2, precision: 94.1, recall: 97.8 },
  { month: 'Feb', accuracy: 96.8, precision: 94.9, recall: 98.1 },
  { month: 'Mar', accuracy: 97.1, precision: 95.6, recall: 98.3 },
  { month: 'Apr', accuracy: 97.4, precision: 96.1, recall: 98.5 },
  { month: 'May', accuracy: 97.8, precision: 96.7, recall: 98.7 },
  { month: 'Jun', accuracy: 98.1, precision: 97.2, recall: 98.9 },
]

const colors = ['#06b6d4', '#a855f7', '#6366f1', '#ec4899']

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-black/80 p-2 rounded-lg border border-white/20 backdrop-blur-xl">
        <p className="text-xs text-white">{payload[0].payload.date || payload[0].payload.month}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-xs">
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export default function AnalyticsPage() {
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
          Analytics
        </h1>
        <p className="text-muted-foreground">Comprehensive threat detection and accuracy metrics</p>
      </motion.div>

      {/* Charts Grid */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        {/* Scan Trends */}
        <GlassCard className="p-6" delay={0.1}>
          <h3 className="text-lg font-display font-bold mb-4">Weekly Scan Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={scanTrendData}>
              <defs>
                <linearGradient id="colorScans" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
              <YAxis stroke="rgba(255,255,255,0.5)" />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="scans"
                stroke="#06b6d4"
                fillOpacity={1}
                fill="url(#colorScans)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </GlassCard>

        {/* Threat Distribution */}
        <GlassCard className="p-6" delay={0.15}>
          <h3 className="text-lg font-display font-bold mb-4">Threat Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={threatDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name} ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {threatDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </GlassCard>

        {/* Accuracy Over Time */}
        <GlassCard className="p-6 lg:col-span-2" delay={0.2}>
          <h3 className="text-lg font-display font-bold mb-4">Model Accuracy Trends</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="month" stroke="rgba(255,255,255,0.5)" />
              <YAxis stroke="rgba(255,255,255,0.5)" domain={[94, 99]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="accuracy"
                stroke="#06b6d4"
                dot={{ fill: '#06b6d4' }}
                name="Accuracy"
              />
              <Line
                type="monotone"
                dataKey="precision"
                stroke="#a855f7"
                dot={{ fill: '#a855f7' }}
                name="Precision"
              />
              <Line
                type="monotone"
                dataKey="recall"
                stroke="#6366f1"
                dot={{ fill: '#6366f1' }}
                name="Recall"
              />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>
      </motion.div>

      {/* Stats */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
      >
        {[
          { label: 'Avg Detection Time', value: '245ms', color: 'cyan' },
          { label: 'Model Accuracy', value: '98.1%', color: 'purple' },
          { label: 'False Positive Rate', value: '0.8%', color: 'green' },
          { label: 'Processing Capacity', value: '10K/min', color: 'pink' },
        ].map((stat, idx) => (
          <GlassCard key={idx} delay={0.35 + idx * 0.05} className="p-6">
            <p className="text-sm text-muted-foreground mb-2">{stat.label}</p>
            <p className={`text-2xl font-display font-bold text-${stat.color}-400`}>
              {stat.value}
            </p>
          </GlassCard>
        ))}
      </motion.div>
    </motion.div>
  )
}
