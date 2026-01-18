import { useState, useEffect, useRef } from 'react';

const TeamMembers = () => {
  const teamMemberSurveyUrl = 'https://www.surveymonkey.com/r/95L75DS?Description=[Description_value]';

  const [titleLoaded, setTitleLoaded] = useState(false);
  const [subtitleLoaded, setSubtitleLoaded] = useState(false);
  const [titleVisible, setTitleVisible] = useState(true);
  const [visibleSections, setVisibleSections] = useState<Set<number>>(new Set());
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);
  const heroRef = useRef<HTMLElement | null>(null);

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

    sectionRefs.current.forEach((section, index) => {
      if (section) {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              const rect = entry.boundingClientRect;
              const viewportHeight = window.innerHeight;
              
              // Check if section is in viewport and not scrolled past the top
              if (entry.isIntersecting && rect.top < viewportHeight * 0.8) {
                setVisibleSections((prev) => new Set(prev).add(index));
              } else {
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
      observers.forEach((observer) => observer.disconnect());
    };
  }, []);

  return (
    <div className="min-h-screen text-white">
      {/* Hero Section - Full Screen */}
      <section ref={heroRef} className="relative overflow-hidden min-h-screen flex items-center justify-center px-6">
        <div className="max-w-6xl mx-auto text-center relative z-10">
          <h1
            className={`text-7xl md:text-9xl mb-12 bg-gradient-to-r from-white to-blue-900 bg-clip-text text-transparent transition-all duration-2000 ease-in-out ${
              titleLoaded && titleVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
            }`}
            style={{ fontWeight: 900, backgroundSize: '200% 200%', animation: 'gradient-shift 3.1s ease infinite', animationDelay: '1.4s', filter: 'drop-shadow(0 0 20px rgba(59, 130, 246, 0.5))' }}
          >
            Team Member Performance Survey
          </h1>
          <p className={`text-2xl md:text-3xl text-blue-100 max-w-3xl mx-auto font-medium transition-all duration-1500 ease-in-out ${
            subtitleLoaded && titleVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
          }`}>
          </p>
        </div>
      </section>


      {/* Performance Section 3 - Survey Purpose Description */}
      <section
        ref={(el) => (sectionRefs.current[3] = el)}
        className={`py-16 px-6 transition-all duration-1000 ${
          visibleSections.has(3) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-md rounded-3xl p-8 md:p-10 border-2 border-transparent bg-clip-padding" style={{ background: 'linear-gradient(#1e293b, #0f172a) padding-box, linear-gradient(to right, #64748b, #1e3a8a) border-box' }}>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-center bg-gradient-to-r from-purple-200 to-blue-300 bg-clip-text" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 4.6s ease infinite', animationDelay: '0.3s', filter: 'drop-shadow(0 0 18px rgba(147, 197, 253, 0.45))' }}>
              Why Your Feedback Matters
            </h2>
            <div className="space-y-5 text-lg text-slate-200 leading-relaxed text-center">
              <p>
                Your insights help us create better experiences for everyone in our internship program. 
                By sharing your perspective, you contribute to:                                                                                                                                                                                                                                                                       


              </p>
              <ul className="space-y-3 max-w-2xl mx-auto text-left">
                <li className="flex items-start">
                  <span className="text-cyan-400 mr-3 text-2xl">✦</span>
                  <span><strong className="text-cyan-300">Improving our processes</strong> to better support interns and team members</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-400 mr-3 text-2xl">✦</span>
                  <span><strong className="text-blue-300">Keeping Talent</strong> make sure high performing interns stay within the company</span>
                </li>
                <li className="flex items-start">
                  <span className="text-purple-400 mr-3 text-2xl">✦</span>
                  <span><strong className="text-purple-300">Shaping future programs</strong> based on real experiences and suggestions</span>
                </li>
              </ul>
              <p className="text-slate-300 mt-6">
                Each survey takes just 1-5 minutes and your responses are completely confidential.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Rewards Section */}
      <section
        ref={(el) => (sectionRefs.current[4] = el)}
        className={`py-16 px-6 transition-all duration-1000 ${
          visibleSections.has(4) ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-bold mb-12 text-center bg-gradient-to-r from-yellow-300 to-orange-400 bg-clip-text text-transparent" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 3.7s ease infinite', animationDelay: '0.7s', filter: 'drop-shadow(0 0 18px rgba(251, 191, 36, 0.45))' }}>
            Earn Rewards for Your Feedback
          </h2>
          
          <div className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-md rounded-3xl p-8 border-2 border-transparent bg-clip-padding mb-12" style={{ background: 'linear-gradient(#1e293b, #0f172a) padding-box, linear-gradient(to right, #64748b, #1e3a8a) border-box' }}>
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="text-center md:text-left">
                <h3 className="text-3xl font-bold bg-gradient-to-r from-yellow-200 via-yellow-400 to-orange-300 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 2.4s ease infinite', animationDelay: '1.1s', filter: 'drop-shadow(0 0 15px rgba(253, 224, 71, 0.4))' }}>Your Points Balance</h3>
                <p className="text-slate-300">Complete surveys to earn points</p>
              </div>
              <div className="relative">
                <div className="text-7xl font-black bg-gradient-to-br from-yellow-400 via-orange-300 to-yellow-500 bg-clip-text ">
                  XXX
                </div>
                <span className="text-2xl text-slate-400 ml-2">pts</span>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-12">
            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border-2 border-transparent bg-clip-padding transition-all duration-500" style={{ background: 'linear-gradient(#1e293b80, #0f172a80) padding-box, linear-gradient(to right, #64748b, #2563eb) border-box' }}>
              <div className="text-center mb-4">
                <div className="text-4xl mb-2">🎁</div>
                <h3 className="text-xl font-semibold bg-gradient-to-r from-green-200 to-emerald-400 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 4.4s ease infinite', animationDelay: '0.5s', filter: 'drop-shadow(0 0 12px rgba(134, 239, 172, 0.35))' }}>$10 Gift Card</h3>
                <p className="text-3xl font-bold bg-gradient-to-r from-white to-green-200 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 3.8s ease infinite', animationDelay: '0.2s', filter: 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.3))' }}>100 pts</p>
              </div>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• Amazon</li>
                <li>• Starbucks</li>
                <li>• iTunes</li>
              </ul>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border-2 border-transparent bg-clip-padding transition-all duration-500" style={{ background: 'linear-gradient(#1e293b80, #0f172a80) padding-box, linear-gradient(to right, #475569, #1e40af) border-box' }}>
              <div className="text-center mb-4">
                <div className="text-4xl mb-2">💳</div>
                <h3 className="text-xl font-semibold bg-gradient-to-r from-blue-200 to-cyan-400 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 2.3s ease infinite', animationDelay: '1.5s', filter: 'drop-shadow(0 0 12px rgba(147, 197, 253, 0.35))' }}>$25 Gift Card</h3>
                <p className="text-3xl font-bold bg-gradient-to-r from-white to-blue-200 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 5.1s ease infinite', animationDelay: '0.4s', filter: 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.3))' }}>250 pts</p>
              </div>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• Target</li>
                <li>• Best Buy</li>
                <li>• Uber Eats</li>
              </ul>
            </div>

            <div className="bg-slate-800/40 backdrop-blur-sm rounded-2xl p-6 border-2 border-transparent bg-clip-padding transition-all duration-500" style={{ background: 'linear-gradient(#1e293b80, #0f172a80) padding-box, linear-gradient(to right, #334155, #1e3a8a) border-box' }}>
              <div className="text-center mb-4">
                <div className="text-4xl mb-2">🏆</div>
                <h3 className="text-xl font-semibold bg-gradient-to-r from-purple-200 to-pink-400 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 4.8s ease infinite', animationDelay: '0.3s', filter: 'drop-shadow(0 0 12px rgba(216, 180, 254, 0.35))' }}>$50 Gift Card</h3>
                <p className="text-3xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent mb-2" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 2.1s ease infinite', animationDelay: '1.3s', filter: 'drop-shadow(0 0 10px rgba(255, 255, 255, 0.3))' }}>500 pts</p>
              </div>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• Apple Store</li>
                <li>• Netflix</li>
                <li>• DoorDash</li>
              </ul>
            </div>
          </div>

          <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border-2 border-transparent bg-clip-padding rounded-2xl p-6" style={{ background: 'linear-gradient(to right, #06b6d410, #3b82f610) padding-box, linear-gradient(to right, #64748b, #1e3a8a) border-box' }}>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-cyan-200 to-blue-400 bg-clip-text text-transparent mb-4 text-center" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 3.5s ease infinite', animationDelay: '0.9s', filter: 'drop-shadow(0 0 15px rgba(103, 232, 249, 0.4))' }}>Earn:</h3>
            <div className="flex justify-center">
              <div className="text-center">
                <div className="text-6xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text mb-3" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 2.2s ease infinite', animationDelay: '1.1s', filter: 'drop-shadow(0 0 22px rgba(103, 232, 249, 0.5))' }}>10 Points!</div>
                <p className="text-xl bg-gradient-to-r from-slate-100 to-blue-200 bg-clip-text text-transparent font-medium" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 4.6s ease infinite', animationDelay: '0.6s', filter: 'drop-shadow(0 0 8px rgba(226, 232, 240, 0.25))' }}>Every time you complete the survey</p>
                <p className="text-sm text-slate-400 mt-2">Keep submitting to accumulate points!</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Survey Feedback Section */}
      <section className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent mb-4" style={{ backgroundSize: '200% 200%', animation: 'gradient-shift 5.4s ease infinite', animationDelay: '0.4s', filter: 'drop-shadow(0 0 18px rgba(216, 180, 254, 0.45))' }}>
              Share Your Feedback
            </h2>
            <p className="text-xl text-slate-300">
              Help us improve by completing the team member survey
            </p>
          </div>

          {/* Survey Panel */}
          <div className="relative min-h-[600px]">
            <div
              className="bg-slate-900/50 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden border border-slate-700/50 transition-all duration-500 opacity-100 translate-y-0"
            >
              <div className="relative w-full" style={{ paddingBottom: '80%' }}>
                <iframe
                  src={teamMemberSurveyUrl}
                  className="absolute inset-0 w-full h-full border-0"
                  title="Team Member Survey"
                  aria-label="Team Member Performance Survey"
                />
              </div>
              <p className="text-center text-slate-400 py-4 text-sm">
                Complete the survey above to provide feedback
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default TeamMembers;
