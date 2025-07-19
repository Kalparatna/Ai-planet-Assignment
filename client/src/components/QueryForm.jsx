export default function QueryForm({ query, setQuery, onSubmit, loading }) {
    return (
      <form onSubmit={onSubmit} className="space-y-4">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your math question..."
          rows={3}
          className="w-full p-3 border rounded-md shadow-sm"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {loading ? 'Solving...' : 'Solve'}
        </button>
      </form>
    );
  }
  