import { ReactNode, useEffect, useState, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useBackendHealth } from '../hooks/useBackendHealth'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const health = useBackendHealth()
  const location = useLocation()
  const [scrollOffset, setScrollOffset] = useState(0)
  const [scrollVelocity, setScrollVelocity] = useState(0)
  const lastScrollY = useRef(0)
  const lastScrollTime = useRef(Date.now())

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  // Track scroll position and velocity
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY
      const currentTime = Date.now()
      
      const deltaY = currentScrollY - lastScrollY.current
      const deltaTime = currentTime - lastScrollTime.current
      
      // Calculate velocity (pixels per millisecond)
      const velocity = deltaTime > 0 ? Math.abs(deltaY / deltaTime) : 0
      
      setScrollOffset(currentScrollY)
      setScrollVelocity(velocity)
      
      lastScrollY.current = currentScrollY
      lastScrollTime.current = currentTime
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      window.removeEventListener('scroll', handleScroll)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-slate-950 to-black relative">
      {/* Animated stars background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="stars"
          style={{
            transform: `translateY(${scrollOffset * 0.5}px)`,
            transition: `transform ${Math.max(100, 300 - scrollVelocity * 100)}ms ease-out`
          }}
        ></div>
        <div 
          className="stars2"
          style={{
            transform: `translateY(${scrollOffset * 0.3}px)`,
            transition: `transform ${Math.max(100, 400 - scrollVelocity * 100)}ms ease-out`
          }}
        ></div>
        <div 
          className="stars3"
          style={{
            transform: `translateY(${scrollOffset * 0.7}px)`,
            transition: `transform ${Math.max(100, 350 - scrollVelocity * 100)}ms ease-out`
          }}
        ></div>
      </div>
      
      {/* Space theme CSS animations */}
      <style>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0.6; }
          50% { opacity: 1; }
        }
        
        .stars, .stars2, .stars3 {
          position: absolute;
          top: -100%;
          left: 0;
          right: 0;
          bottom: -100%;
          width: 100%;
          height: 300%;
          background: transparent;
          will-change: transform;
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
          animation: twinkle 3s ease-in-out infinite;
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
          animation: twinkle 4s ease-in-out infinite;
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
          animation: twinkle 5s ease-in-out infinite;
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
            <div className="flex items-center space-x-1">
              <Link
                to="/"
                className={`relative flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300 group overflow-hidden ${
                  location.pathname === '/' 
                    ? 'text-white bg-gradient-to-r from-blue-600/20 to-purple-600/20' 
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <span className="relative z-10">Dashboard</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/0 via-purple-600/0 to-pink-600/0 group-hover:from-blue-600/20 group-hover:via-purple-600/20 group-hover:to-pink-600/20 transition-all duration-500 rounded-lg"></div>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-pink-500/30 blur-md"></div>
                </div>
              </Link>
              <Link
                to="/interns"
                className={`relative flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300 group overflow-hidden ${
                  location.pathname === '/interns' 
                    ? 'text-white bg-gradient-to-r from-blue-600/20 to-purple-600/20' 
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <span className="relative z-10">Interns</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/0 via-purple-600/0 to-pink-600/0 group-hover:from-blue-600/20 group-hover:via-purple-600/20 group-hover:to-pink-600/20 transition-all duration-500 rounded-lg"></div>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-pink-500/30 blur-md"></div>
                </div>
              </Link>
              <Link
                to="/team-members"
                className={`relative flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300 group overflow-hidden ${
                  location.pathname === '/team-members' 
                    ? 'text-white bg-gradient-to-r from-blue-600/20 to-purple-600/20' 
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <span className="relative z-10">Team Members</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/0 via-purple-600/0 to-pink-600/0 group-hover:from-blue-600/20 group-hover:via-purple-600/20 group-hover:to-pink-600/20 transition-all duration-500 rounded-lg"></div>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-pink-500/30 blur-md"></div>
                </div>
              </Link>
              <Link
                to="/managers"
                className={`relative flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-300 group overflow-hidden ${
                  location.pathname === '/managers' 
                    ? 'text-white bg-gradient-to-r from-blue-600/20 to-purple-600/20' 
                    : 'text-slate-300 hover:text-white'
                }`}
              >
                <span className="relative z-10">Managers</span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/0 via-purple-600/0 to-pink-600/0 group-hover:from-blue-600/20 group-hover:via-purple-600/20 group-hover:to-pink-600/20 transition-all duration-500 rounded-lg"></div>
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-500/30 via-purple-500/30 to-pink-500/30 blur-md"></div>
                </div>
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

