import { FileText, Globe, Database, Cpu, MessageSquare } from './Icons';

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
        default:
          return source;
      }
    };

    const formatSolution = (text) => {
      return text.split('\n').map((line, index) => {
        // Handle markdown-style formatting
        if (line.startsWith('## ')) {
          return <h3 key={index} className="text-lg font-semibold mt-4 mb-2 text-gray-900">{line.replace('## ', '')}</h3>;
        }
        if (line.startsWith('### ')) {
          return <h4 key={index} className="text-md font-medium mt-3 mb-1 text-gray-800">{line.replace('### ', '')}</h4>;
        }
        if (line.startsWith('**') && line.endsWith('**')) {
          return <p key={index} className="font-semibold mt-2 mb-1">{line.replace(/\*\*/g, '')}</p>;
        }
        if (line.trim() === '') {
          return <br key={index} />;
        }
        return <p key={index} className="mb-1 leading-relaxed">{line}</p>;
      });
    };

    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Solution</h2>
          <div className="flex items-center space-x-3">
            <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getSourceColor(solution.source)}`}>
              {getSourceIcon(solution.source)}
              <span>{getSourceLabel(solution.source)}</span>
            </div>
            <div className="text-sm text-gray-600">
              {Math.round(solution.confidence * 100)}% confidence
            </div>
          </div>
        </div>

        <div className="prose prose-sm max-w-none text-gray-700">
          {formatSolution(solution.solution)}
        </div>

        {solution.references?.length > 0 && (
          <div className="mt-6 pt-4 border-t border-gray-200">
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

        <div className="mt-6 pt-4 border-t border-gray-200 flex justify-between items-center">
          <button
            onClick={onFeedbackClick}
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 transition-colors duration-200"
          >
            <MessageSquare className="h-4 w-4 mr-1" />
            Provide Feedback
          </button>
          
          {solution.source === 'pdf_upload' && (
            <div className="text-xs text-purple-600 bg-purple-50 px-2 py-1 rounded">
              ✓ Answer from your uploaded PDF
            </div>
          )}
        </div>
      </div>
    );
  }
  