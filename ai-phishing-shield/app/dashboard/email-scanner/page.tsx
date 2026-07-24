'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Mail, Upload, Code, Loader2, Send } from 'lucide-react'
import { GlassCard } from '@/components/cards/GlassCard'
import toast from 'react-hot-toast'
import { scanEmail, uploadImage } from '@/services/api'

export default function EmailScannerPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'paste' | 'upload' | 'html'>('paste')
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)

  const handleAnalyze = async () => {
    setIsLoading(true)
    try {
      let result;
      if (activeTab === 'upload') {
        if (!file) {
          toast.error('Please select an image file first.')
          setIsLoading(false)
          return
        }
        const formData = new FormData()
        formData.append('file', file)
        result = await uploadImage(formData)
      } else {
        if (!email.trim()) {
          toast.error('Please enter email text to analyze.')
          setIsLoading(false)
          return
        }
        result = await scanEmail(email)
      }
      
      // Store results in localStorage so results page can display it
      localStorage.setItem('shield_analysis_result', JSON.stringify(result))
      localStorage.setItem('shield_email_source', activeTab === 'upload' ? 'Extracted OCR content of uploaded image' : email)
      
      toast.success('Analysis completed!')
      router.push('/dashboard/results')
    } catch (error: any) {
      console.error(error)
      const errorMsg = error.response?.data?.detail || 'Analysis failed. Please check backend status.'
      toast.error(errorMsg)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast.error('File size exceeds 10MB limit.')
        return
      }
      setFile(selectedFile)
      toast.success(`Selected file: ${selectedFile.name}`)
    }
  }

  const tabs = [
    { id: 'paste' as const, label: 'Paste Email', icon: Mail },
    { id: 'upload' as const, label: 'Upload Screenshot', icon: Upload },
    { id: 'html' as const, label: 'Paste HTML', icon: Code },
  ]

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
          Email Scanner
        </h1>
        <p className="text-muted-foreground">
          Analyze emails in real-time to detect phishing threats and malicious content
        </p>
      </motion.div>

      {/* Main Scanner Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <GlassCard className="p-8">
          {/* Tabs */}
          <div className="flex gap-4 mb-8 border-b border-white/10 pb-4">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <motion.button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                      : 'text-muted-foreground hover:text-foreground hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-semibold">{tab.label}</span>
                </motion.button>
              )
            })}
          </div>

          {/* Tab Content */}
          <div className="space-y-4">
            {activeTab === 'paste' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <label className="block text-sm font-semibold mb-2">
                  Paste Email Content
                </label>
                <textarea
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Paste the entire email content here, including headers..."
                  className="w-full h-64 p-4 rounded-lg bg-white/5 border border-white/10 text-foreground placeholder-muted-foreground focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all duration-200 resize-none"
                />
              </motion.div>
            )}

            {activeTab === 'upload' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <label className="block text-sm font-semibold mb-2">
                  Upload Email Image / Screenshot
                </label>
                <div className="relative border-2 border-dashed border-cyan-500/50 rounded-lg p-12 text-center hover:border-cyan-400/75 hover:bg-cyan-500/5 transition-all duration-200 cursor-pointer group">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex flex-col items-center gap-3">
                    <div className="p-3 rounded-lg bg-gradient-cyan-purple/10 group-hover:bg-gradient-cyan-purple/20 transition-colors">
                      <Upload className="w-8 h-8 text-cyan-400" />
                    </div>
                    <div>
                      <p className="font-semibold mb-1">
                        {file ? file.name : 'Click to upload or drag and drop'}
                      </p>
                      <p className="text-sm text-muted-foreground">PNG, JPG, or GIF up to 10MB</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'html' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="space-y-4"
              >
                <label className="block text-sm font-semibold mb-2">
                  Paste Email HTML
                </label>
                <textarea
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Paste the HTML source of the email..."
                  className="w-full h-64 p-4 rounded-lg bg-white/5 border border-white/10 text-foreground placeholder-muted-foreground focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all duration-200 resize-none font-mono text-sm"
                />
              </motion.div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <motion.button
              onClick={handleAnalyze}
              disabled={isLoading || (activeTab !== 'upload' && !email.trim()) || (activeTab === 'upload' && !file)}
              whileHover={{ scale: isLoading ? 1 : 1.02 }}
              whileTap={{ scale: isLoading ? 1 : 0.98 }}
              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-gradient-cyan-purple text-background font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-2xl hover:shadow-cyan-500/40 transition-all duration-300"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Analyze Email
                </>
              )}
            </motion.button>

            <motion.button
              onClick={() => {
                setEmail('')
                setFile(null)
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-white/10 text-foreground hover:bg-white/5 transition-all duration-300"
            >
              Clear
            </motion.button>
          </div>
        </GlassCard>
      </motion.div>

      {/* Tips */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        {[
          {
            title: 'Deep Analysis',
            description: 'We analyze headers, content, and embedded resources for threats',
          },
          {
            title: 'Advanced Detection',
            description: 'ML models detect phishing patterns, spoofing, and malicious links',
          },
          {
            title: 'Fast Results',
            description: 'Get comprehensive threat assessment in milliseconds',
          },
        ].map((tip, idx) => (
          <GlassCard key={idx} delay={0.25 + idx * 0.1} className="p-6 text-center">
            <h3 className="font-display font-bold mb-2">{tip.title}</h3>
            <p className="text-sm text-muted-foreground">{tip.description}</p>
          </GlassCard>
        ))}
      </motion.div>
    </motion.div>
  )
}
