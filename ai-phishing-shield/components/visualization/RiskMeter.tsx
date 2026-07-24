'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface RiskMeterProps {
  score: number
  label?: string
  delay?: number
  size?: 'sm' | 'md' | 'lg'
}

export const RiskMeter = ({
  score,
  label = 'Risk Score',
  delay = 0,
  size = 'lg',
}: RiskMeterProps) => {
  const [displayScore, setDisplayScore] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      let current = 0
      const increment = score / 30
      const counter = setInterval(() => {
        current += increment
        if (current >= score) {
          setDisplayScore(score)
          clearInterval(counter)
        } else {
          setDisplayScore(Math.floor(current))
        }
      }, 16)
      return () => clearInterval(counter)
    }, delay * 1000)

    return () => clearTimeout(timer)
  }, [score, delay])

  const getRiskColor = (s: number) => {
    if (s >= 80) return 'from-red-500 to-red-600'
    if (s >= 60) return 'from-orange-500 to-red-500'
    if (s >= 40) return 'from-amber-500 to-orange-500'
    return 'from-cyan-500 to-blue-500'
  }

  const getRiskLabel = (s: number) => {
    if (s >= 80) return 'CRITICAL'
    if (s >= 60) return 'HIGH'
    if (s >= 40) return 'MEDIUM'
    return 'LOW'
  }

  const sizeClasses = {
    sm: 'w-32 h-32',
    md: 'w-48 h-48',
    lg: 'w-64 h-64',
  }

  const circumference = 2 * Math.PI * 90
  const strokeDashoffset = circumference - (displayScore / 100) * circumference

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, delay }}
      className="flex flex-col items-center gap-4"
    >
      <div className={`${sizeClasses[size]} relative`}>
        <svg
          viewBox="0 0 200 200"
          className="w-full h-full transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx="100"
            cy="100"
            r="90"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
          />
          {/* Progress circle */}
          <circle
            cx="100"
            cy="100"
            r="90"
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-100"
          />
          <defs>
            <linearGradient
              id="gradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="100%"
            >
              <stop
                offset="0%"
                stopColor={
                  displayScore >= 80
                    ? '#ef4444'
                    : displayScore >= 60
                      ? '#f97316'
                      : displayScore >= 40
                        ? '#eab308'
                        : '#22c55e'
                }
              />
              <stop
                offset="100%"
                stopColor={
                  displayScore >= 80
                    ? '#ec4899'
                    : displayScore >= 60
                      ? '#dc2626'
                      : displayScore >= 40
                        ? '#f97316'
                        : '#10b981'
                }
              />
            </linearGradient>
          </defs>
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-4xl md:text-5xl font-display font-bold gradient-text">
            {displayScore}%
          </div>
          <div className="text-xs text-muted-foreground mt-1">Risk Score</div>
        </div>
      </div>

      <div className="text-center">
        <p className="text-lg font-semibold text-white">{label}</p>
        <p
          className={`text-sm font-bold mt-2 ${
            displayScore >= 80
              ? 'text-red-400'
              : displayScore >= 60
                ? 'text-orange-400'
                : displayScore >= 40
                  ? 'text-yellow-400'
                  : 'text-green-400'
          }`}
        >
          {getRiskLabel(displayScore)}
        </p>
      </div>
    </motion.div>
  )
}
