import QueryForm from './components/QueryForm'
import SolutionDisplay from './components/SolutionDisplay'
import FeedbackForm from './components/FeedbackForm'
import HistoryList from './components/HistoryList'
import PDFTab from './components/PDFTab'
import { useState, useEffect } from 'react'
import { Calculator, FileText, History } from './components/Icons'

function App() {
  const [query, setQuery] = useState('')
  const [solution, setSolution] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [rating, setRating] = useState(0)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)
  const [improvedSolution, setImprovedSolution] = useState(null)
  const [queryHistory, setQueryHistory] = useState([])
  const [activeTab, setActiveTab] = useState('query')
  const [selectedPDF, setSelectedPDF] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSolution(null);
    setShowFeedback(false);
    setFeedbackSubmitted(false);
    setImprovedSolution(null);

    try {
      const response = await fetch('http://localhost:8000/math/solve', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to get a solution');
      }

      const data = await response.json();
      setSolution(data);
      setQueryHistory([...queryHistory, { query, solution: data }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/feedback/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query_id: solution.query_id,
          original_solution: solution.solution,
          feedback,
          rating,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit feedback');
      }

      const data = await response.json();
      setImprovedSolution(data.improved_solution);
      setFeedbackSubmitted(true);
      setShowFeedback(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryItemClick = (item) => {
    setQuery(item.query);
    setSolution(item.solution);
    setActiveTab('query'); // Switch to query tab when selecting from history
  };

  const handlePDFSelect = (pdf) => {
    setSelectedPDF(pdf);
  };

  const tabs = [
    {
      id: 'query',
      label: 'Math Query',
      icon: Calculator,
      description: 'Ask mathematical questions'
    },
    {
      id: 'pdf',
      label: 'PDF Documents',
      icon: FileText,
      description: 'Upload and manage PDFs'
    },
    {
      id: 'history',
      label: 'History',
      icon: History,
      description: 'View query history'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold text-blue-700">Math Routing Agent</h1>
        <p className="text-gray-600">
          Ask any math question for step-by-step help • Upload PDFs for document-based queries
        </p>
        {selectedPDF && (
          <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
            <FileText className="h-4 w-4 mr-1" />
            PDF Selected: {selectedPDF.filename}
          </div>
        )}
      </header>

      <main className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    group relative min-w-0 flex-1 overflow-hidden bg-white py-4 px-6 text-sm font-medium text-center hover:bg-gray-50 focus:z-10
                    ${activeTab === tab.id
                      ? 'text-blue-600 border-b-2 border-blue-500'
                      : 'text-gray-500 hover:text-gray-700'
                    }
                  `}
                >
                  <Icon className={`
                    h-5 w-5 mx-auto mb-1
                    ${activeTab === tab.id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'}
                  `} />
                  <span className="block">{tab.label}</span>
                  <span className="block text-xs text-gray-400 mt-1">{tab.description}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'query' && (
            <div className="space-y-6">
              <QueryForm 
                query={query} 
                setQuery={setQuery} 
                onSubmit={handleSubmit} 
                loading={loading}
                selectedPDF={selectedPDF}
              />
              
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-600">{error}</p>
                </div>
              )}

              {solution && (
                <SolutionDisplay
                  solution={solution}
                  onFeedbackClick={() => setShowFeedback(true)}
                />
              )}

              {showFeedback && !feedbackSubmitted && (
                <FeedbackForm
                  feedback={feedback}
                  setFeedback={setFeedback}
                  rating={rating}
                  setRating={setRating}
                  onSubmit={handleFeedbackSubmit}
                  onCancel={() => setShowFeedback(false)}
                  loading={loading}
                />
              )}

              {feedbackSubmitted && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-700 font-medium">Thank you for your feedback!</p>
                  {improvedSolution && (
                    <div className="mt-4">
                      <h3 className="font-semibold text-green-800 mb-2">Improved Solution:</h3>
                      <div className="text-green-700">
                        {improvedSolution.split('\n').map((line, index) => (
                          <p key={index} className="mb-1">{line}</p>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'pdf' && (
            <PDFTab 
              onPDFSelect={handlePDFSelect}
              selectedPDF={selectedPDF}
            />
          )}

          {activeTab === 'history' && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Query History</h3>
                <p className="text-gray-600">
                  View your previous math queries and solutions. Click on any item to reuse it.
                </p>
              </div>
              <HistoryList 
                history={queryHistory} 
                onSelect={handleHistoryItemClick} 
              />
            </div>
          )}
        </div>
      </main>

      <footer className="mt-8 text-center text-sm text-gray-500">
        <p>Powered by FastAPI, React & LangChain | Agentic-RAG Architecture with PDF Support</p>
      </footer>
    </div>
  )
}

export default App
