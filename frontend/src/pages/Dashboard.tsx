import { useBackendHealth } from '../hooks/useBackendHealth'

function Dashboard() {
  const health = useBackendHealth()

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Dashboard content placeholder - ready for implementation
        </p>
        
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
                  Cannot connect to backend at http://localhost:8000
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

