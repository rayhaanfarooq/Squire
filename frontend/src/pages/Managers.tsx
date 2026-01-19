import { useState, useEffect, useRef } from 'react';

const Managers = () => {
  const managerSurveyUrl = 'https://www.surveymonkey.com/r/96ZDST6';

  const [titleLoaded, setTitleLoaded] = useState(false);
  const [subtitleLoaded, setSubtitleLoaded] = useState(false);
  const [titleVisible, setTitleVisible] = useState(true);
  const [visibleSections, setVisibleSections] = useState<Set<number>>(new Set());
  const [sectionDirections, setSectionDirections] = useState<Map<number, 'down' | 'up'>>(new Map());
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);
  const heroRef = useRef<HTMLElement | null>(null);
  const lastScrollY = useRef(0);

  useEffect(() => {
    // Initial fade in
    const titleTimer = setTimeout(() => {
      setTitleLoaded(true);
    }, 500);
    
    const subtitleTimer = setTimeout(() => {
      setSubtitleLoaded(true);
    }, 1500);
    
    return () => {
      clearTimeout(titleTimer);
      clearTimeout(subtitleTimer);
    };
  }, []);

  // Scroll-based visibility for hero section
  useEffect(() => {
    const handleScroll = () => {
      if (heroRef.current) {
        const rect = heroRef.current.getBoundingClientRect();
        const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
        setTitleVisible(isVisible);
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Check initial state

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  useEffect(() => {
    const observers: IntersectionObserver[] = [];

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDirection = currentScrollY > lastScrollY.current ? 'down' : 'up';
      lastScrollY.current = currentScrollY;
      
      sectionRefs.current.forEach((section, index) => {
        if (section) {
          const rect = section.getBoundingClientRect();
          const isVisible = rect.top < window.innerHeight * 0.8 && rect.bottom > 0;
          
          if (isVisible) {
            setSectionDirections((prev) => {
              const newMap = new Map(prev);
              newMap.set(index, scrollDirection);
              return newMap;
            });
          }
        }
      });
    };

    window.addEventListener('scroll', handleScroll);

    sectionRefs.current.forEach((section, index) => {
      if (section) {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              const rect = entry.boundingClientRect;
              const viewportHeight = window.innerHeight;
              const currentScrollY = window.scrollY;
              const scrollDirection = currentScrollY > lastScrollY.current ? 'down' : 'up';
              
              // Show when scrolling down and entering viewport
              if (entry.isIntersecting && rect.top < viewportHeight * 0.8) {
                setVisibleSections((prev) => new Set(prev).add(index));
                setSectionDirections((prev) => {
                  const newMap = new Map(prev);
                  newMap.set(index, scrollDirection);
                  return newMap;
                });
              } 
              // Hide sooner when scrolling up - when top of element goes above 20% of viewport
              else if (scrollDirection === 'up' && rect.top < viewportHeight * 0.2) {
                setVisibleSections((prev) => {
                  const newSet = new Set(prev);
                  newSet.delete(index);
                  return newSet;
                });
              }
              // Hide normally when not intersecting and scrolling down
              else if (!entry.isIntersecting) {
                setVisibleSections((prev) => {
                  const newSet = new Set(prev);
                  newSet.delete(index);
                  return newSet;
                });
              }
            });
          },
          {
            threshold: [0, 0.1, 0.2, 0.3, 0.4, 0.5],
            rootMargin: '-10% 0px -20% 0px',
          }
        );

        observer.observe(section);
        observers.push(observer);
      }
    });

    return () => {
      window.removeEventListener('scroll', handleScroll);
      observers.forEach((observer) => observer.disconnect());
    };
  }, []);

  return (
    <div className="min-h-screen text-white">
      {/* Hero Section - Full Screen */}
      <section ref={heroRef} className="relative overflow-hidden min-h-screen flex items-center justify-center px-6">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-950/40 via-slate-900/40 to-purple-950/40 opacity-50"></div>
        <div className="max-w-6xl mx-auto text-center relative z-10">
          <h1
            className={`text-6xl md:text-8xl lg:text-9xl mb-8 bg-gradient-to-r from-white via-blue-100 to-blue-400 bg-clip-text text-transparent transition-all duration-1000 ease-out animate-gradient-1 ${
              titleLoaded && titleVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
            }`}
            style={{ fontWeight: 900, lineHeight: '1.1', filter: 'drop-shadow(0 0 30px rgba(59, 130, 246, 0.4))' }}
          >
            Manager Performance Survey
          </h1>
          <p className={`text-xl md:text-2xl text-blue-100/90 max-w-3xl mx-auto font-light leading-relaxed transition-all duration-700 ease-out ${
            subtitleLoaded && titleVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
          }`}>
            Help us enhance our program through your valuable insights
          </p>
        </div>
      </section>


      {/* Performance Section 3 - Survey Purpose Description */}
      <section
        ref={(el) => (sectionRefs.current[3] = el)}
        className={`py-20 px-6 transition-all duration-1000 ease-out ${
          visibleSections.has(3)
            ? 'opacity-100 translate-x-0 translate-y-0'
            : sectionDirections.get(3) === 'up'
            ? 'opacity-0 -translate-y-32'
            : 'opacity-0 translate-x-32'
        }`}
      >
        <div className="max-w-5xl mx-auto">
          <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl rounded-3xl p-10 md:p-14 border border-slate-700/50 shadow-2xl hover:shadow-blue-500/10 transition-all duration-500 hover:border-slate-600/50">
            <h2 className="text-4xl md:text-5xl font-bold mb-10 text-center bg-gradient-to-r from-blue-200 via-cyan-200 to-purple-300 bg-clip-text text-transparent animate-gradient-2">
              Why Your Feedback Matters
            </h2>
            <div className="space-y-8">
              <p className="text-lg md:text-xl text-slate-200/90 leading-relaxed text-center max-w-3xl mx-auto">
                Your insights help us create better experiences for everyone in our program. 
                By sharing your perspective, you contribute to:
              </p>
              <ul className="space-y-5 max-w-2xl mx-auto">
                <li className="flex items-start group hover:translate-x-2 transition-transform duration-300">
                  <span className="text-cyan-400 mr-4 text-xl mt-1 group-hover:scale-110 transition-transform duration-300">✦</span>
                  <span className="text-base md:text-lg text-slate-200/90"><strong className="text-cyan-300 font-semibold">Improving our processes</strong> to better support interns and team members</span>
                </li>
                <li className="flex items-start group hover:translate-x-2 transition-transform duration-300">
                  <span className="text-blue-400 mr-4 text-xl mt-1 group-hover:scale-110 transition-transform duration-300">✦</span>
                  <span className="text-base md:text-lg text-slate-200/90"><strong className="text-blue-300 font-semibold">Keeping talent</strong> ensuring high-performing interns stay within the company</span>
                </li>
                <li className="flex items-start group hover:translate-x-2 transition-transform duration-300">
                  <span className="text-purple-400 mr-4 text-xl mt-1 group-hover:scale-110 transition-transform duration-300">✦</span>
                  <span className="text-base md:text-lg text-slate-200/90"><strong className="text-purple-300 font-semibold">Shaping future programs</strong> based on real experiences and suggestions</span>
                </li>
              </ul>
              <div className="pt-6 text-center">
                <p className="text-base text-slate-300/80 inline-flex items-center gap-2">
                  <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Takes just 1-5 minutes • Completely confidential
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Rewards Section */}
      <section
        ref={(el) => (sectionRefs.current[4] = el)}
        className="py-20 px-6"
      >
        <div className="max-w-6xl mx-auto">
          <h2 className={`text-4xl md:text-5xl font-bold mb-16 text-center bg-gradient-to-r from-yellow-300 via-orange-300 to-pink-400 bg-clip-text text-transparent animate-gradient-wave transition-all duration-1000 ease-out ${
            visibleSections.has(4)
              ? 'opacity-100 translate-y-0'
              : sectionDirections.get(4) === 'up'
              ? 'opacity-0 -translate-y-12'
              : 'opacity-0 translate-y-12'
          }`}
          style={{ transitionDelay: visibleSections.has(4) ? '0ms' : (sectionDirections.get(4) === 'up' ? '1000ms' : '0ms') }}>
            Earn Rewards for Your Feedback
          </h2>
          
          <div className={`bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-xl rounded-3xl p-8 md:p-10 border border-slate-700/50 shadow-2xl mb-12 hover:shadow-yellow-500/10 transition-all duration-1000 ease-out ${
            visibleSections.has(4)
              ? 'opacity-100 translate-y-0 scale-100'
              : sectionDirections.get(4) === 'up'
              ? 'opacity-0 -translate-y-20 scale-95'
              : 'opacity-0 translate-y-20 scale-95'
          } hover:border-slate-600/50`} style={{ transitionDelay: visibleSections.has(4) ? '200ms' : (sectionDirections.get(4) === 'up' ? '800ms' : '200ms') }}>
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="text-center md:text-left">
                <h3 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-orange-300 bg-clip-text text-transparent mb-2 animate-gradient-pulse">
                  Your Points Balance
                </h3>
                <p className="text-slate-300/80 text-base">Complete surveys to earn points</p>
              </div>
              <div className="relative flex items-baseline">
                <div className="text-7xl md:text-8xl font-black bg-gradient-to-br from-yellow-400 via-orange-400 to-yellow-500 bg-clip-text text-transparent">
                  XXX
                </div>
                <span className="text-2xl md:text-3xl text-slate-400/80 ml-2">pts</span>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-14">
            <div 
              onMouseEnter={() => setHoveredCard(0)}
              onMouseLeave={() => setHoveredCard(null)}
              className={`bg-slate-800/40 backdrop-blur-sm rounded-2xl p-7 border border-slate-700/50 cursor-pointer transition-all duration-1000 ease-out ${
                hoveredCard === 0 ? 'transform -translate-y-2 shadow-2xl shadow-green-500/20 border-green-500/50' : 'hover:border-slate-600/50'
              } ${
                visibleSections.has(4)
                  ? 'opacity-100 translate-x-0 translate-y-0 scale-100'
                  : sectionDirections.get(4) === 'up'
                  ? 'opacity-0 -translate-x-20 -translate-y-12 scale-90'
                  : 'opacity-0 -translate-x-20 translate-y-12 scale-90'
              }`}
              style={{ transitionDelay: visibleSections.has(4) ? '400ms' : (sectionDirections.get(4) === 'up' ? '600ms' : '400ms') }}
            >
              <div className="text-center mb-5">
                <div className={`text-5xl mb-3 transition-transform duration-300 ${
                  hoveredCard === 0 ? 'scale-110' : ''
                }`}>🎁</div>
                <h3 className="text-xl font-semibold bg-gradient-to-r from-green-300 to-emerald-400 bg-clip-text text-transparent mb-3 animate-gradient-3">
                  $10 Gift Card
                </h3>
                <p className="text-4xl font-bold bg-gradient-to-r from-white to-green-200 bg-clip-text text-transparent mb-2 animate-gradient-1">
                  100 pts
                </p>
              </div>
              <ul className="text-sm text-slate-300/90 space-y-2">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  Amazon
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  Starbucks
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                  iTunes
                </li>
              </ul>
            </div>

            <div 
              onMouseEnter={() => setHoveredCard(1)}
              onMouseLeave={() => setHoveredCard(null)}
              className={`bg-slate-800/40 backdrop-blur-sm rounded-2xl p-7 border border-slate-700/50 cursor-pointer transition-all duration-1000 ease-out ${
                hoveredCard === 1 ? 'transform -translate-y-2 shadow-2xl shadow-blue-500/20 border-blue-500/50' : 'hover:border-slate-600/50'
              } ${
                visibleSections.has(4)
                  ? 'opacity-100 translate-y-0 scale-100'
                  : sectionDirections.get(4) === 'up'
                  ? 'opacity-0 -translate-y-20 scale-90'
                  : 'opacity-0 translate-y-20 scale-90'
              }`}
              style={{ transitionDelay: visibleSections.has(4) ? '600ms' : (sectionDirections.get(4) === 'up' ? '400ms' : '600ms') }}
            >
              <div className="text-center mb-5">
                <div className={`text-5xl mb-3 transition-transform duration-300 ${
                  hoveredCard === 1 ? 'scale-110' : ''
                }`}>💳</div>
                <h3 className="text-xl font-semibold bg-gradient-to-r from-blue-300 to-cyan-400 bg-clip-text text-transparent mb-3 animate-gradient-2">
                  $25 Gift Card
                </h3>
                <p className="text-4xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent mb-2 animate-gradient-wave">
                  250 pts
                </p>
              </div>
              <ul className="text-sm text-slate-300/90 space-y-2">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  Target
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  Best Buy
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                  Uber Eats
                </li>
              </ul>
            </div>

            <div 
              onMouseEnter={() => setHoveredCard(2)}
              onMouseLeave={() => setHoveredCard(null)}
              className={`bg-slate-800/40 backdrop-blur-sm rounded-2xl p-7 border border-slate-700/50 cursor-pointer transition-all duration-1000 ease-out ${
                hoveredCard === 2 ? 'transform -translate-y-2 shadow-2xl shadow-purple-500/20 border-purple-500/50' : 'hover:border-slate-600/50'
              } ${
                visibleSections.has(4)
                  ? 'opacity-100 translate-x-0 translate-y-0 scale-100'
                  : sectionDirections.get(4) === 'up'
                  ? 'opacity-0 translate-x-20 -translate-y-12 scale-90'
                  : 'opacity-0 translate-x-20 translate-y-12 scale-90'
              }`}
              style={{ transitionDelay: visibleSections.has(4) ? '800ms' : (sectionDirections.get(4) === 'up' ? '200ms' : '800ms') }}
            >
              <div className="text-center mb-5">
                <div className={`text-5xl mb-3 transition-transform duration-300 ${
                  hoveredCard === 2 ? 'scale-110' : ''
                }`}>🏆</div>
                <h3 className="text-xl font-semibold bg-gradient-to-r from-purple-300 to-pink-400 bg-clip-text text-transparent mb-3 animate-gradient-pulse">
                  $50 Gift Card
                </h3>
                <p className="text-4xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent mb-2 animate-gradient-3">
                  500 pts
                </p>
              </div>
              <ul className="text-sm text-slate-300/90 space-y-2">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                  Apple Store
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                  Netflix
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                  DoorDash
                </li>
              </ul>
            </div>
          </div>

          <div className={`bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-2xl p-8 md:p-10 hover:border-cyan-500/50 transition-all duration-1000 ease-out hover:shadow-cyan-500/20 shadow-xl ${
            visibleSections.has(4)
              ? 'opacity-100 translate-y-0 scale-100'
              : sectionDirections.get(4) === 'up'
              ? 'opacity-0 -translate-y-20 scale-95'
              : 'opacity-0 translate-y-20 scale-95'
          } hover:border-slate-600/50`} style={{ transitionDelay: visibleSections.has(4) ? '1000ms' : (sectionDirections.get(4) === 'up' ? '0ms' : '1000ms') }}>
            <div className="flex justify-center">
              <div className="text-center">
                <h3 className="text-2xl font-bold bg-gradient-to-r from-cyan-200 to-blue-300 bg-clip-text text-transparent mb-5 animate-gradient-1">Earn Per Survey</h3>
                <div className="inline-flex items-baseline gap-2 mb-4">
                  <div className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent animate-gradient-wave">
                    10
                  </div>
                  <span className="text-3xl md:text-4xl text-cyan-300/80 font-semibold">Points!</span>
                </div>
                <p className="text-lg md:text-xl text-slate-100/90 font-medium mb-2">
                  Every time you complete the survey
                </p>
                <p className="text-sm text-slate-400/80">
                  Keep submitting to accumulate points and earn rewards
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Survey Feedback Section */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-300 via-blue-300 to-cyan-300 bg-clip-text text-transparent mb-5 animate-gradient-2">
              Share Your Feedback
            </h2>
            <p className="text-lg md:text-xl text-slate-300/90 max-w-2xl mx-auto">
              Help us improve by completing the manager survey
            </p>
          </div>

          {/* Survey Panel */}
          <div className="relative min-h-[600px]">
            <div className="bg-slate-900/40 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden border border-slate-700/50 hover:border-slate-600/50 transition-all duration-500">
              <div className="relative w-full" style={{ paddingBottom: '80%' }}>
                <iframe
                  src={managerSurveyUrl}
                  className="absolute inset-0 w-full h-full border-0"
                  title="Manager Survey"
                  aria-label="Manager Performance Survey"
                />
              </div>
              <div className="bg-slate-800/50 py-4 px-6">
                <p className="text-center text-slate-400/80 text-sm">
                  Complete the survey above to provide feedback and earn 10 points
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Managers;
