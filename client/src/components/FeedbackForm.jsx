export default function FeedbackForm({
    feedback,
    setFeedback,
    rating,
    setRating,
    onSubmit,
    onCancel,
    loading,
  }) {
    return (
      <div className="mt-6 bg-gray-50 p-4 rounded shadow">
        <h2 className="text-lg font-medium mb-2">Your Feedback</h2>
        <div className="flex space-x-1 text-yellow-500 mb-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <span
              key={star}
              onClick={() => setRating(star)}
              className={`cursor-pointer ${
                rating >= star ? 'text-yellow-500' : 'text-gray-300'
              }`}
            >
              ★
            </span>
          ))}
        </div>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="What could be improved?"
          rows={3}
          className="w-full p-2 border rounded mb-2"
        />
        <div className="flex space-x-2">
          <button
            onClick={onSubmit}
            disabled={loading || rating === 0}
            className="px-3 py-1 bg-blue-600 text-white rounded disabled:opacity-50"
          >
            Submit
          </button>
          <button
            onClick={onCancel}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }
  