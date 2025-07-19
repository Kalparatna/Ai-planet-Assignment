export default function SolutionDisplay({ solution, onFeedbackClick }) {
    return (
      <div className="mt-6 bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-2">Solution</h2>
        <div className="text-sm text-gray-700">
          {solution.solution.split('\n').map((line, index) => (
            <p key={index}>{line}</p>
          ))}
        </div>
        <div className="mt-2 flex justify-between items-center">
          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
            Source: {solution.source}
          </span>
          <span className="text-sm text-gray-600">
            Confidence: {Math.round(solution.confidence * 100)}%
          </span>
        </div>
        {solution.references?.length > 0 && (
          <div className="mt-4">
            <h3 className="font-medium">References:</h3>
            <ul className="list-disc list-inside">
              {solution.references.map((ref, i) => (
                <li key={i}>
                  <a
                    href={ref}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 underline"
                  >
                    {ref}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
        <button
          onClick={onFeedbackClick}
          className="mt-4 text-sm text-blue-600 hover:underline"
        >
          Provide Feedback
        </button>
      </div>
    );
  }
  