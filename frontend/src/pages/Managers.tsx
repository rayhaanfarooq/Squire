import { useState, useEffect, useRef } from 'react';

const Managers = () => {
  const managerSurveyUrl = 'https://www.surveymonkey.com/r/96ZDST6';

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
              if (entry.isIntersecting) {
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
            threshold: 0.2,
            rootMargin: '0px 0px -100px 0px',
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
            style={{ fontWeight: 900 }}
          >
            Manager Performance Survey
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
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-center bg-gradient-to-r from-purple-200 to-blue-300 bg-clip-text">
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
          <h2 className="text-4xl md:text-5xl font-bold mb-12 text-center bg-gradient-to-r from-yellow-300 to-orange-400 bg-clip-text text-transparent">
            Earn Rewards for Your Feedback
          </h2>
          
          <div className="bg-gradient-to-br from-slate-800/60 to-slate-900/60 backdrop-blur-md rounded-3xl p-8 border-2 border-transparent bg-clip-padding mb-12" style={{ background: 'linear-gradient(#1e293b, #0f172a) padding-box, linear-gradient(to right, #64748b, #1e3a8a) border-box' }}>
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="text-center md:text-left">
                <h3 className="text-3xl font-bold text-yellow-300 mb-2">Your Points Balance</h3>
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
                <h3 className="text-xl font-semibold text-green-300 mb-2">$10 Gift Card</h3>
                <p className="text-3xl font-bold text-white mb-2">100 pts</p>
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
                <h3 className="text-xl font-semibold text-blue-300 mb-2">$25 Gift Card</h3>
                <p className="text-3xl font-bold text-white mb-2">250 pts</p>
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
                <h3 className="text-xl font-semibold text-purple-300 mb-2">$50 Gift Card</h3>
                <p className="text-3xl font-bold text-white mb-2">500 pts</p>
              </div>
              <ul className="text-sm text-slate-300 space-y-1">
                <li>• Apple Store</li>
                <li>• Netflix</li>
                <li>• DoorDash</li>
              </ul>
            </div>
          </div>

          <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border-2 border-transparent bg-clip-padding rounded-2xl p-6" style={{ background: 'linear-gradient(to right, #06b6d410, #3b82f610) padding-box, linear-gradient(to right, #64748b, #1e3a8a) border-box' }}>
            <h3 className="text-2xl font-bold text-cyan-300 mb-4 text-center">Earn:</h3>
            <div className="flex justify-center">
              <div className="text-center">
                <div className="text-6xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text mb-3">10 Points!</div>
                <p className="text-xl text-slate-200 font-medium">Every time you complete the survey</p>
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
            <h2 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-300 to-blue-300 bg-clip-text text-transparent mb-4">
              Share Your Feedback
            </h2>
            <p className="text-xl text-slate-300">
              Help us improve by completing the manager survey
            </p>
          </div>

          {/* Survey Panel */}
          <div className="relative min-h-[600px]">
            <div
              className="bg-slate-900/50 backdrop-blur-sm rounded-2xl shadow-2xl overflow-hidden border border-slate-700/50 transition-all duration-500 opacity-100 translate-y-0"
            >
              <div className="relative w-full" style={{ paddingBottom: '80%' }}>
                <iframe
                  src={managerSurveyUrl}
                  className="absolute inset-0 w-full h-full border-0"
                  title="Manager Survey"
                  aria-label="Manager Performance Survey"
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

export default Managers;
