import { useState } from 'react'
import { useBackendHealth } from '../hooks/useBackendHealth'
import { api } from '../services/api'

function Dashboard() {
  const health = useBackendHealth()
  const [isLoading, setIsLoading] = useState(false)
  const [prResult, setPrResult] = useState<string | null>(null)
  const [meetingResult, setMeetingResult] = useState<string | null>(null)
  const [managerResult, setManagerResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleTriggerAgents = async () => {
    setIsLoading(true)
    setError(null)
    setPrResult(null)
    setMeetingResult(null)
    setManagerResult(null)

    try {
      const response = await api.triggerAgents()
      
      // Parse the result - the agents output "hello world" and "world hello"
      // We'll extract these from the response
      const resultText = response.result || ''
      const lowerText = resultText.toLowerCase()
      
      // Simple parsing - look for "hello world" and "world hello" in the response
      // PRAgent and MeetingAgent both output "hello world"
      if (lowerText.includes('hello world')) {
        setPrResult('hello world')
        setMeetingResult('hello world')
      }
      
      // ManagerAgent outputs "world hello"
      if (lowerText.includes('world hello')) {
        setManagerResult('world hello')
      }
      
      // If we can't parse, show the full result
      if (!lowerText.includes('hello world') && !lowerText.includes('world hello')) {
        setPrResult(resultText)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger agents')
      console.error('Error triggering agents:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Dashboard content placeholder - ready for implementation
        </p>
        
        {/* Agent Trigger Section */}
        <div className="mt-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Agent Workflow
          </h2>
          
          <button
            onClick={handleTriggerAgents}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            {isLoading ? 'Running Agents...' : 'Trigger Agents'}
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {/* Results Display */}
          {(prResult || meetingResult || managerResult) && (
            <div className="mt-4 space-y-3">
              {prResult && (
                <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <p className="text-sm font-medium text-green-800 dark:text-green-200 mb-1">
                    PRAgent & MeetingAgent Result:
                  </p>
                  <p className="text-lg font-mono text-green-900 dark:text-green-100">
                    {prResult}
                  </p>
                </div>
              )}
              
              {managerResult && (
                <div className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                  <p className="text-sm font-medium text-purple-800 dark:text-purple-200 mb-1">
                    ManagerAgent Result:
                  </p>
                  <p className="text-lg font-mono text-purple-900 dark:text-purple-100">
                    {managerResult}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Backend Health Status Card */}
        <div className="mt-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
            Backend Status
          </h2>
          <div className="flex items-center space-x-3">
            <div
              className={`w-3 h-3 rounded-full ${
                health.status === 'healthy'
                  ? 'bg-green-500'
                  : health.status === 'checking'
                  ? 'bg-yellow-500 animate-pulse'
                  : 'bg-red-500'
              }`}
            />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Status: {health.status === 'healthy' ? '✅ Healthy' : health.status === 'checking' ? '🔄 Checking...' : '❌ Unhealthy'}
              </p>
              {health.status === 'healthy' && (
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {health.service || 'API'} v{health.version || 'unknown'}
                </p>
              )}
              {health.status === 'unhealthy' && (
                <p className="text-xs text-red-600 dark:text-red-400">
                  Cannot connect to backend at http://localhost:8002
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

