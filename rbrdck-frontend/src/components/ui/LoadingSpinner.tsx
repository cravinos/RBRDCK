// components/ui/LoadingSpinner.tsx

'use client'

import React from 'react'

interface LoadingSpinnerProps {
  size?: number // Size in pixels
  color?: string // Color of the spinner
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ size = 24, color = '#4F46E5' }) => {
  return (
    <div className="flex items-center justify-center">
      <svg
        className="animate-spin"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke={color}
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill={color}
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        ></path>
      </svg>
    </div>
  )
}

export default LoadingSpinner
