import { useState, useEffect } from 'react'
import { api } from '../services/api'

interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'checking'
  version?: string
  service?: string
}

/**
 * Custom hook to check backend health status
 */
export function useBackendHealth() {
  const [health, setHealth] = useState<HealthStatus>({ status: 'checking' })

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await api.healthCheck()
        setHealth({
          status: 'healthy',
          version: response.version,
          service: response.service,
        })
      } catch (error) {
        setHealth({ status: 'unhealthy' })
      }
    }

    // Check immediately
    checkHealth()

    // Check every 5 seconds
    const interval = setInterval(checkHealth, 5000)

    return () => clearInterval(interval)
  }, [])

  return health
}

