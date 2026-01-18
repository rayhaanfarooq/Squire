import { ReactNode, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useBackendHealth } from '../hooks/useBackendHealth'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const health = useBackendHealth()
  const location = useLocation()

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-slate-950 to-black relative">
      {/* Animated stars background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="stars"></div>
        <div className="stars2"></div>
        <div className="stars3"></div>
      </div>
      
      {/* Space theme CSS animations */}
      <style>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
        
        @keyframes moveStars {
          from { transform: translateY(0); }
          to { transform: translateY(-200px); }
        }
        
        .stars, .stars2, .stars3 {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          width: 100%;
          height: 100%;
          background: transparent;
        }
        
        .stars {
          background-image: 
            radial-gradient(3px 3px at 20px 30px, rgba(255, 255, 255, 0.95), transparent),
            radial-gradient(3px 3px at 60px 70px, rgba(255, 255, 255, 0.9), transparent),
            radial-gradient(2px 2px at 50px 50px, rgba(200, 220, 255, 0.85), transparent),
            radial-gradient(2px 2px at 130px 80px, rgba(255, 240, 200, 0.9), transparent),
            radial-gradient(3px 3px at 90px 10px, rgba(255, 255, 255, 0.95), transparent),
            radial-gradient(2px 2px at 150px 120px, rgba(220, 230, 255, 0.85), transparent),
            radial-gradient(2px 2px at 180px 45px, rgba(255, 250, 220, 0.9), transparent);
          background-repeat: repeat;
          background-size: 200px 200px;
          animation: twinkle 3s ease-in-out infinite, moveStars 40s linear infinite;
        }
        
        .stars2 {
          background-image: 
            radial-gradient(2px 2px at 40px 60px, rgba(255, 255, 255, 0.9), transparent),
            radial-gradient(2px 2px at 110px 90px, rgba(200, 220, 255, 0.85), transparent),
            radial-gradient(2px 2px at 160px 40px, rgba(255, 240, 200, 0.85), transparent),
            radial-gradient(1px 1px at 80px 110px, rgba(255, 255, 255, 0.8), transparent),
            radial-gradient(2px 2px at 30px 140px, rgba(220, 230, 255, 0.9), transparent),
            radial-gradient(1px 1px at 170px 75px, rgba(255, 250, 220, 0.85), transparent);
          background-repeat: repeat;
          background-size: 200px 200px;
          animation: twinkle 4s ease-in-out infinite, moveStars 50s linear infinite;
          animation-delay: 1s;
        }
        
        .stars3 {
          background-image: 
            radial-gradient(2px 2px at 75px 25px, rgba(255, 255, 255, 0.95), transparent),
            radial-gradient(2px 2px at 180px 100px, rgba(200, 220, 255, 0.9), transparent),
            radial-gradient(1px 1px at 120px 65px, rgba(255, 240, 200, 0.85), transparent),
            radial-gradient(2px 2px at 45px 135px, rgba(255, 255, 255, 0.9), transparent),
            radial-gradient(1px 1px at 155px 15px, rgba(220, 230, 255, 0.85), transparent);
          background-repeat: repeat;
          background-size: 200px 200px;
          animation: twinkle 5s ease-in-out infinite, moveStars 60s linear infinite;
          animation-delay: 2s;
        }

        html {
          scroll-behavior: smooth;
        }
      `}</style>

      <nav className="fixed top-0 left-0 right-0 bg-slate-900/80 backdrop-blur-md shadow-lg border-b border-slate-700/50 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link
                to="/"
                className="flex items-center px-4 text-xl font-semibold text-white"
              >
                Squire
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/interns"
                className="flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Interns
              </Link>
              <Link
                to="/team-members"
                className="flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Team Members
              </Link>
              <Link
                to="/managers"
                className="flex items-center px-3 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
              >
                Managers
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
                <span className="text-xs text-slate-400">
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
      <div className="h-16"></div>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 relative z-10">
        {children}
      </main>
    </div>
  )
}

export default Layout

