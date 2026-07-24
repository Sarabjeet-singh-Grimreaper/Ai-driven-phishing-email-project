'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { CheckCircle2, Star } from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'
import { fetchModels, ModelData } from '@/services/api'
import toast from 'react-hot-toast'

export default function ModelsPage() {
  const [models, setModels] = useState<ModelData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadModels = async () => {
      try {
        const data = await fetchModels()
        setModels(data)
      } catch (error) {
        toast.error('Failed to load comparison models from backend.')
        console.error(error)
      } finally {
        setLoading(false)
      }
    }
    loadModels()
  }, [])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <div className="w-8 h-8 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin" />
        <p className="text-muted-foreground">Gathering model benchmarks from the ML backend...</p>
      </div>
    )
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
      >
        <h1 className="text-3xl md:text-4xl font-display font-bold gradient-text mb-2">
          ML Models
        </h1>
        <p className="text-muted-foreground">Compare performance metrics across detection models</p>
      </motion.div>

      {/* Model Comparison Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <GlassCard className="p-8 overflow-x-auto">
          <div className="w-full">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-4 px-4 font-semibold text-muted-foreground">Model</th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">
                    Accuracy
                  </th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">
                    Precision
                  </th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">
                    Recall
                  </th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">F1</th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">ROC</th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">
                    Latency
                  </th>
                  <th className="text-center py-4 px-4 font-semibold text-muted-foreground">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {models.map((model, idx) => (
                  <motion.tr
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.15 + idx * 0.05 }}
                    className={`border-b border-white/10 hover:bg-white/5 transition-colors ${
                      model.highlight ? 'bg-cyan-500/10' : ''
                    }`}
                  >
                    <td className="py-4 px-4 font-semibold">
                      <div className="flex items-center gap-2">
                        {model.highlight && <Star className="w-4 h-4 text-yellow-400" />}
                        {model.name}
                      </div>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="font-semibold text-cyan-400">{model.accuracy}%</span>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="font-semibold text-purple-400">{model.precision}%</span>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="font-semibold text-pink-400">{model.recall}%</span>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="font-semibold text-indigo-400">{model.f1}%</span>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="font-semibold text-green-400">{model.roc}</span>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span className="text-muted-foreground">{model.latency}</span>
                    </td>
                    <td className="text-center py-4 px-4">
                      <span
                        className={`text-xs font-bold px-2 py-1 rounded-full ${
                          model.status === 'Production'
                            ? 'bg-green-500/20 text-green-400'
                            : model.status === 'Testing'
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-gray-500/20 text-gray-400'
                        }`}
                      >
                        {model.status}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      </motion.div>

      {/* Model Details Grid */}
      <motion.div
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.25 }}
      >
        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-4">Current Production Model</h3>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0 mt-1" />
              <div>
                <p className="font-semibold">Random Forest Hybrid Ensemble</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Ensemble classifier combined with custom metadata scaler and TF-IDF feature vocabulary dictionaries.
                </p>
              </div>
            </div>
            <div className="pt-4 border-t border-white/10">
              <p className="text-xs text-muted-foreground mb-2">Key Features:</p>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li>• Real-time email header analysis</li>
                <li>• Content-based threat detection</li>
                <li>• URL reputation scanning</li>
                <li>• Sentiment analysis for urgency detection</li>
              </ul>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-8">
          <h3 className="text-lg font-display font-bold mb-4">Model Architecture</h3>
          <div className="space-y-4">
            <div className="p-4 rounded-lg bg-white/5 border border-white/10 font-mono text-xs">
              <p className="text-cyan-400">INPUT LAYER</p>
              <p className="text-muted-foreground">↓ Email TF-IDF text features (4000 dims) + Scaled metadata (7 features)</p>
              <p className="text-purple-400">ENSEMBLE ESTIMATORS</p>
              <p className="text-muted-foreground">↓ Tuned Decision Trees</p>
              <p className="text-pink-400">METADATA CORRELATION</p>
              <p className="text-muted-foreground">↓ MinMaxScaler structural integration</p>
              <p className="text-green-400">OUTPUT (Binary Phishing vs Ham)</p>
            </div>
          </div>
        </GlassCard>
      </motion.div>

      {/* Performance Metrics */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-4 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.35 }}
      >
        {[
          { label: 'True Positive Rate', value: '98.7%', color: 'green' },
          { label: 'False Positive Rate', value: '0.8%', color: 'red' },
          { label: 'Model Version', value: 'v3.2.1', color: 'blue' },
          { label: 'Last Updated', value: '2 days ago', color: 'yellow' },
        ].map((metric, idx) => (
          <GlassCard key={idx} delay={0.4 + idx * 0.05} className="p-6">
            <p className="text-xs text-muted-foreground mb-2">{metric.label}</p>
            <p className={`text-2xl font-display font-bold text-${metric.color}-400`}>
              {metric.value}
            </p>
          </GlassCard>
        ))}
      </motion.div>
    </motion.div>
  )
}
