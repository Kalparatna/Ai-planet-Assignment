import { FileText, Globe, Database, Cpu, MessageSquare } from './Icons';
import MathSolutionRenderer from './MathSolutionRenderer';

export default function SolutionDisplay({ solution, onFeedbackClick }) {
    const getSourceIcon = (source) => {
      switch (source) {
        case 'pdf_upload':
          return <FileText className="h-4 w-4" />;
        case 'web_search':
          return <Globe className="h-4 w-4" />;
        case 'knowledge_base':
          return <Database className="h-4 w-4" />;
        case 'generated':
          return <Cpu className="h-4 w-4" />;
        case 'hitl_improved':
          return <MessageSquare className="h-4 w-4" />;
        default:
          return <Database className="h-4 w-4" />;
      }
    };

    const getSourceColor = (source) => {
      switch (source) {
        case 'pdf_upload':
          return 'bg-purple-100 text-purple-800';
        case 'web_search':
          return 'bg-blue-100 text-blue-800';
        case 'knowledge_base':
          return 'bg-green-100 text-green-800';
        case 'generated':
          return 'bg-orange-100 text-orange-800';
        case 'hitl_improved':
          return 'bg-indigo-100 text-indigo-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    const getSourceLabel = (source) => {
      switch (source) {
        case 'pdf_upload':
          return 'PDF Document';
        case 'web_search':
          return 'Web Search';
        case 'knowledge_base':
          return 'Knowledge Base';
        case 'generated':
          return 'AI Generated';
        case 'hitl_improved':
          return 'Community Improved';
        default:
          return source;
      }
    };

    return (
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Header with source info */}
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Solution</h2>
            <div className="flex items-center space-x-3">
              <div className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium ${getSourceColor(solution.source)}`}>
                {getSourceIcon(solution.source)}
                <span>{getSourceLabel(solution.source)}</span>
              </div>
              <div className="text-sm text-gray-600 bg-white px-2 py-1 rounded border">
                {Math.round(solution.confidence * 100)}% confidence
              </div>
            </div>
          </div>
          
          {solution.source === 'hitl_improved' && (
            <div className="mt-2 text-xs text-indigo-600 bg-indigo-50 px-2 py-1 rounded inline-block">
              🧠 Improved by community feedback
            </div>
          )}
          
          {solution.source === 'pdf_upload' && (
            <div className="mt-2 text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded inline-block">
              📄 Answer from your uploaded PDF
            </div>
          )}
        </div>

        {/* Main content - use structured renderer if available */}
        <div className="p-0">
          {solution.sections && solution.sections.length > 0 ? (
            <MathSolutionRenderer response={solution} />
          ) : (
            <div className="p-6">
              <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                {solution.solution}
              </div>
            </div>
          )}
        </div>

        {/* References section */}
        {solution.references?.length > 0 && (
          <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
            <h3 className="font-medium text-gray-900 mb-2 flex items-center">
              <FileText className="h-4 w-4 mr-1" />
              References:
            </h3>
            <ul className="space-y-1">
              {solution.references.map((ref, i) => (
                <li key={i} className="text-sm">
                  {ref.startsWith('http') ? (
                    <a
                      href={ref}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      {ref}
                    </a>
                  ) : (
                    <span className="text-gray-600">{ref}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Footer with feedback button */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex justify-between items-center">
            <button
              onClick={onFeedbackClick}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors duration-200"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              Provide Feedback
            </button>
            
            <div className="text-xs text-gray-500">
              Help improve this solution with your feedback
            </div>
          </div>
        </div>
      </div>
    );
  }
  