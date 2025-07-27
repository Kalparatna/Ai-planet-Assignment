import { FileText, Search } from './Icons';

export default function QueryForm({ query, setQuery, onSubmit, loading, selectedPDF }) {
    return (
      <form onSubmit={onSubmit} className="space-y-4">
        {selectedPDF && (
          <div className="flex items-center space-x-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <FileText className="h-5 w-5 text-blue-600" />
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900">
                PDF Context: {selectedPDF.filename}
              </p>
              <p className="text-xs text-blue-700">
                Questions will search this document first
              </p>
            </div>
          </div>
        )}
        
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={selectedPDF 
              ? "Ask a question about your uploaded PDF or any math topic..."
              : "Enter your math question..."
            }
            rows={3}
            className="w-full p-3 border rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {selectedPDF ? (
              <span>✓ PDF selected • Will search document content first</span>
            ) : (
              <span>Will search knowledge base → web → generate solution</span>
            )}
          </div>
          
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Solving...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Solve
              </>
            )}
          </button>
        </div>
      </form>
    );
  }
  