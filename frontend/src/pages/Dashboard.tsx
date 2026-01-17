import { useState } from 'react'
import { useBackendHealth } from '../hooks/useBackendHealth'
import { api } from '../services/api'

interface ManagerReport {
  report?: {
    executive_summary?: string
    pr_insights?: any
    meeting_insights?: any
    recommendations?: string[]
    action_items?: string[]
    detailed_pr_summaries?: any[]
    detailed_meeting_summaries?: any[]
  }
  timestamp?: string
  status?: string
}

function Dashboard() {
  const health = useBackendHealth()
  const [isLoading, setIsLoading] = useState(false)
  const [prResult, setPrResult] = useState<string | null>(null)
  const [meetingResult, setMeetingResult] = useState<string | null>(null)
  const [managerResult, setManagerResult] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoadingReport, setIsLoadingReport] = useState(false)
  const [report, setReport] = useState<ManagerReport | null>(null)
  const [reportError, setReportError] = useState<string | null>(null)

  const handleTriggerAgents = async () => {
    setIsLoading(true)
    setError(null)
    setPrResult(null)
    setMeetingResult(null)
    setManagerResult(null)

    try {
      // Use the analysis start endpoint instead of SAM gateway
      const response = await api.startAnalysis(3)
      
      // Show success message
      setPrResult('Analysis workflow started')
      setMeetingResult('PR Agent and Meeting Agent are analyzing in parallel')
      setManagerResult('Manager Agent will synthesize results when both complete')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis workflow')
      console.error('Error starting analysis:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGetReport = async () => {
    setIsLoadingReport(true)
    setReportError(null)
    setReport(null)

    try {
      const reportData = await api.getManagerReport()
      setReport(reportData)
    } catch (err) {
      setReportError(err instanceof Error ? err.message : 'Failed to fetch report')
      console.error('Error fetching report:', err)
    } finally {
      setIsLoadingReport(false)
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
        
        {/* Manager Report Section */}
        <div className="mt-6 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Manager Report
          </h2>
          
          <button
            onClick={handleGetReport}
            disabled={isLoadingReport}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            {isLoadingReport ? 'Loading Report...' : 'Get Manager Report'}
          </button>

          {reportError && (
            <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-sm text-red-600 dark:text-red-400">{reportError}</p>
            </div>
          )}

          {report && (
            <div className="mt-6 space-y-4">
              {/* Report Status Badge */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Report Available
                  </span>
                </div>
                {report.timestamp && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    Generated: {new Date(report.timestamp).toLocaleString()}
                  </span>
                )}
              </div>

              {/* Executive Summary - report.report.report is the actual report object */}
              {report.report?.report?.executive_summary && (
                <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-800 rounded-xl shadow-sm">
                  <div className="flex items-center space-x-2 mb-3">
                    <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-lg font-bold text-blue-900 dark:text-blue-100">
                      Executive Summary
                    </h3>
                  </div>
                  <div className="text-sm text-blue-800 dark:text-blue-200 whitespace-pre-wrap leading-relaxed">
                    {report.report.report.executive_summary}
                  </div>
                </div>
              )}

              {/* Insights Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* PR Insights */}
                {report.report?.report?.pr_insights && (
                  <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-200 dark:border-green-800 rounded-xl shadow-sm">
                    <div className="flex items-center space-x-2 mb-4">
                      <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                      </svg>
                      <h3 className="text-lg font-bold text-green-900 dark:text-green-100">
                        PR Insights
                      </h3>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-green-700 dark:text-green-300">Total PRs:</span>
                          <span className="font-bold text-lg text-green-900 dark:text-green-100">{report.report.report.pr_insights.total_prs || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-green-700 dark:text-green-300">Files Changed:</span>
                          <span className="font-bold text-lg text-green-900 dark:text-green-100">{report.report.report.pr_insights.total_files_changed || 0}</span>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-green-700 dark:text-green-300">High Complexity:</span>
                          <span className="font-bold text-lg text-green-900 dark:text-green-100">{report.report.report.pr_insights.high_complexity_count || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-green-700 dark:text-green-300">High Risk:</span>
                          <span className="font-bold text-lg text-green-900 dark:text-green-100">{report.report.report.pr_insights.high_risk_count || 0}</span>
                        </div>
                      </div>
                    </div>
                    <div className="mt-4 pt-4 border-t border-green-200 dark:border-green-700">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-green-700 dark:text-green-300">Code Changes:</span>
                        <span className="font-semibold text-green-900 dark:text-green-100">
                          <span className="text-green-600 dark:text-green-400">+{report.report.report.pr_insights.total_additions || 0}</span>
                          {' / '}
                          <span className="text-red-600 dark:text-red-400">-{report.report.report.pr_insights.total_deletions || 0}</span>
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Meeting Insights */}
                {report.report?.report?.meeting_insights && (
                  <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-2 border-purple-200 dark:border-purple-800 rounded-xl shadow-sm">
                    <div className="flex items-center space-x-2 mb-4">
                      <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <h3 className="text-lg font-bold text-purple-900 dark:text-purple-100">
                        Meeting Insights
                      </h3>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-purple-700 dark:text-purple-300">Documents:</span>
                          <span className="font-bold text-lg text-purple-900 dark:text-purple-100">{report.report.report.meeting_insights.documents_analyzed || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-purple-700 dark:text-purple-300">Action Items:</span>
                          <span className="font-bold text-lg text-purple-900 dark:text-purple-100">{report.report.report.meeting_insights.total_action_items || 0}</span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-purple-700 dark:text-purple-300">Decisions:</span>
                          <span className="font-bold text-lg text-purple-900 dark:text-purple-100">{report.report.report.meeting_insights.total_decisions || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-purple-700 dark:text-purple-300">Attendees:</span>
                          <span className="font-bold text-lg text-purple-900 dark:text-purple-100">{report.report.report.meeting_insights.total_attendees || 0}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendations */}
              {report.report?.report?.recommendations && report.report.report.recommendations.length > 0 && (
                <div className="p-6 bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border-2 border-yellow-200 dark:border-yellow-800 rounded-xl shadow-sm">
                  <div className="flex items-center space-x-2 mb-4">
                    <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    <h3 className="text-lg font-bold text-yellow-900 dark:text-yellow-100">
                      Recommendations
                    </h3>
                  </div>
                  <ul className="space-y-2">
                    {report.report.report.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start space-x-3 text-sm text-yellow-800 dark:text-yellow-200">
                        <span className="text-yellow-600 dark:text-yellow-400 mt-1">•</span>
                        <span className="flex-1">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Action Items */}
              {report.report?.report?.action_items && report.report.report.action_items.length > 0 && (
                <div className="p-6 bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 border-2 border-orange-200 dark:border-orange-800 rounded-xl shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <svg className="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      <h3 className="text-lg font-bold text-orange-900 dark:text-orange-100">
                        Action Items
                      </h3>
                    </div>
                    <span className="text-xs font-semibold px-2 py-1 bg-orange-200 dark:bg-orange-800 text-orange-900 dark:text-orange-100 rounded-full">
                      {report.report.report.action_items.length}
                    </span>
                  </div>
                  <ul className="space-y-2 max-h-64 overflow-y-auto">
                    {report.report.report.action_items.map((item, idx) => (
                      <li key={idx} className="flex items-start space-x-3 text-sm text-orange-800 dark:text-orange-200">
                        <span className="text-orange-600 dark:text-orange-400 mt-1">•</span>
                        <span className="flex-1">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Detailed PR Summaries */}
              {report.report?.report?.detailed_pr_summaries && report.report.report.detailed_pr_summaries.length > 0 && (
                <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-200 dark:border-green-800 rounded-xl shadow-sm">
                  <div className="flex items-center space-x-2 mb-4">
                    <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-lg font-bold text-green-900 dark:text-green-100">
                      PR Analysis Details
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {report.report.report.detailed_pr_summaries.map((prSummary, idx) => (
                      <div key={idx} className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-green-200 dark:border-green-700">
                        <div className="flex items-center justify-between mb-2">
                          <a 
                            href={prSummary.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm font-semibold text-green-700 dark:text-green-300 hover:underline"
                          >
                            PR #{prSummary.pr_number}: {prSummary.title}
                          </a>
                          <div className="flex space-x-2">
                            <span className={`text-xs px-2 py-1 rounded ${prSummary.complexity === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : prSummary.complexity === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}`}>
                              {prSummary.complexity} complexity
                            </span>
                            <span className={`text-xs px-2 py-1 rounded ${prSummary.risk_level === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : prSummary.risk_level === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}`}>
                              {prSummary.risk_level} risk
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-green-800 dark:text-green-200 leading-relaxed">
                          {prSummary.summary}
                        </p>
                        {prSummary.patch_analysis && prSummary.patch_analysis.features_detected && prSummary.patch_analysis.features_detected.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-green-200 dark:border-green-700">
                            <p className="text-xs font-semibold text-green-700 dark:text-green-300 mb-1">Features Detected:</p>
                            <div className="flex flex-wrap gap-2">
                              {prSummary.patch_analysis.features_detected.map((feature, fIdx) => (
                                <span key={fIdx} className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded">
                                  {feature}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detailed Meeting Summaries */}
              {report.report?.report?.detailed_meeting_summaries && report.report.report.detailed_meeting_summaries.length > 0 && (
                <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-2 border-purple-200 dark:border-purple-800 rounded-xl shadow-sm">
                  <div className="flex items-center space-x-2 mb-4">
                    <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-lg font-bold text-purple-900 dark:text-purple-100">
                      Meeting Analysis Details
                    </h3>
                  </div>
                  <div className="space-y-4">
                    {report.report.report.detailed_meeting_summaries.map((meetingSummary, idx) => (
                      <div key={idx} className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-purple-200 dark:border-purple-700">
                        <div className="mb-2">
                          <a 
                            href={meetingSummary.doc_url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm font-semibold text-purple-700 dark:text-purple-300 hover:underline"
                          >
                            Meeting Document
                          </a>
                        </div>
                        <p className="text-sm text-purple-800 dark:text-purple-200 leading-relaxed mb-3">
                          {meetingSummary.summary}
                        </p>
                        {meetingSummary.action_items && meetingSummary.action_items.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-purple-200 dark:border-purple-700">
                            <p className="text-xs font-semibold text-purple-700 dark:text-purple-300 mb-1">Action Items:</p>
                            <ul className="list-disc list-inside text-xs text-purple-800 dark:text-purple-200 space-y-1">
                              {meetingSummary.action_items.slice(0, 5).map((item, aIdx) => (
                                <li key={aIdx}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Show raw report if structure is unexpected */}
              {!report.report?.report && (
                <div className="p-6 bg-gray-50 dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl">
                  <pre className="text-xs text-gray-700 dark:text-gray-300 overflow-auto">
                    {JSON.stringify(report, null, 2)}
                  </pre>
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

