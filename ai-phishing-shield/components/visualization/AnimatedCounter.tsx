'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface AnimatedCounterProps {
  value: number
  label: string
  suffix?: string
  prefix?: string
  delay?: number
  className?: string
}

export const AnimatedCounter = ({
  value,
  label,
  suffix = '',
  prefix = '',
  delay = 0,
  className = '',
}: AnimatedCounterProps) => {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    const timer = setTimeout(() => {
      let current = 0
      const increment = value / 30
      const counter = setInterval(() => {
        current += increment
        if (current >= value) {
          setDisplayValue(value)
          clearInterval(counter)
        } else {
          setDisplayValue(Math.floor(current))
        }
      }, 16)
      return () => clearInterval(counter)
    }, delay * 1000)

    return () => clearTimeout(timer)
  }, [value, delay])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay }}
      className={className}
    >
      <div className="text-3xl md:text-4xl font-display font-bold gradient-text">
        {prefix}
        {displayValue.toLocaleString()}
        {suffix}
      </div>
      <p className="text-sm text-muted-foreground mt-2">{label}</p>
    </motion.div>
  )
}
