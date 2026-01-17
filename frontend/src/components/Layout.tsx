import { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useBackendHealth } from '../hooks/useBackendHealth'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const health = useBackendHealth()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link
                to="/"
                className="flex items-center px-4 text-xl font-semibold text-gray-900 dark:text-white"
              >
                Squire
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              >
                Dashboard
              </Link>
              <Link
                to="/interns"
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              >
                Interns
              </Link>
              <div className="flex items-center space-x-2 px-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    health.status === 'healthy'
                      ? 'bg-green-500'
                      : health.status === 'checking'
                      ? 'bg-yellow-500 animate-pulse'
                      : 'bg-red-500'
                  }`}
                  title={
                    health.status === 'healthy'
                      ? `Backend is healthy (${health.service || 'API'} v${health.version || 'unknown'})`
                      : health.status === 'checking'
                      ? 'Checking backend status...'
                      : 'Backend is not responding'
                  }
                />
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  {health.status === 'healthy'
                    ? 'Backend'
                    : health.status === 'checking'
                    ? 'Checking...'
                    : 'Backend Offline'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}

export default Layout

