/**
 * API service module - placeholder for API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002'

export const api = {
  /**
   * Generic fetch wrapper
   */
  async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`)
    }

    return response.json()
  },

  /**
   * Health check endpoint
   */
  async healthCheck() {
    return this.request<{ status: string; service: string; version: string }>('/health')
  },

  /**
   * Trigger SAM agents workflow
   */
  async triggerAgents() {
    return this.request<{ success: boolean; result: string; raw_response?: any }>('/api/agents/trigger', {
      method: 'POST',
    })
  },
}

