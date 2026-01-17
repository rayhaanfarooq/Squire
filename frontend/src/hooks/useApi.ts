import { useState, useEffect } from 'react'
import { api } from '../services/api'

/**
 * Custom hook for API calls - placeholder
 */
export function useApi<T>(
  endpoint: string,
  options?: RequestInit
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)
        const result = await api.request<T>(endpoint, options)
        setData(result)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'))
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [endpoint])

  return { data, loading, error }
}

