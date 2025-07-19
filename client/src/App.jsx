import QueryForm from './components/QueryForm'
import SolutionDisplay from './components/SolutionDisplay'
import FeedbackForm from './components/FeedbackForm'
import HistoryList from './components/HistoryList'
import { useState, useEffect } from 'react'

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
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6 font-sans">
      <header className="text-center mb-8">
        <h1 className="text-3xl font-bold text-blue-700">Math Routing Agent</h1>
        <p className="text-gray-600">Ask any math question for step-by-step help</p>
      </header>

      <main className="max-w-3xl mx-auto bg-white p-6 rounded shadow">
        <QueryForm query={query} setQuery={setQuery} onSubmit={handleSubmit} loading={loading} />
        
        {error && <p className="text-red-600 mt-4">{error}</p>}

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
          <div className="mt-6 text-green-700">
            <p>Thank you for your feedback!</p>
            {improvedSolution && (
              <div className="mt-4 p-4 bg-green-50 rounded">
                <h3 className="font-semibold">Improved Solution:</h3>
                {improvedSolution.split('\n').map((line, index) => (
                  <p key={index}>{line}</p>
                ))}
              </div>
            )}
          </div>
        )}

        <HistoryList history={queryHistory} onSelect={handleHistoryItemClick} />
      </main>

      <footer className="mt-8 text-center text-sm text-gray-500">
        <p>Powered by FastAPI, React & LangChain | Agentic-RAG Architecture</p>
      </footer>
    </div>
  )
}

export default App
