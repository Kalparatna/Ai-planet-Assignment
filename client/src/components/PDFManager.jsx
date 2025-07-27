import React, { useState, useEffect } from 'react';
import { FileText, Trash2, Eye, Calendar, Hash } from './Icons';

const PDFManager = ({ onPDFSelect }) => {
  const [pdfs, setPdfs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPDF, setSelectedPDF] = useState(null);

  useEffect(() => {
    fetchPDFs();
  }, []);

  const fetchPDFs = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/pdf/list');
      const result = await response.json();
      
      if (response.ok) {
        setPdfs(result.pdfs || []);
      } else {
        throw new Error('Failed to fetch PDFs');
      }
    } catch (err) {
      console.error('Error fetching PDFs:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePDF = async (fileId, filename) => {
    if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/pdf/${fileId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setPdfs(pdfs.filter(pdf => pdf.file_id !== fileId));
        if (selectedPDF === fileId) {
          setSelectedPDF(null);
          if (onPDFSelect) {
            onPDFSelect(null);
          }
        }
      } else {
        throw new Error('Failed to delete PDF');
      }
    } catch (err) {
      console.error('Error deleting PDF:', err);
      alert('Failed to delete PDF. Please try again.');
    }
  };

  const handleSelectPDF = (pdf) => {
    const newSelection = selectedPDF === pdf.file_id ? null : pdf.file_id;
    setSelectedPDF(newSelection);
    
    if (onPDFSelect) {
      onPDFSelect(newSelection ? pdf : null);
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-600">Loading PDFs...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-700">Error: {error}</p>
        <button
          onClick={fetchPDFs}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  if (pdfs.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
        <p className="text-lg font-medium mb-2">No PDFs uploaded yet</p>
        <p className="text-sm">Upload a PDF to get started with document-based queries</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-800">
          Uploaded PDFs ({pdfs.length})
        </h3>
        <button
          onClick={fetchPDFs}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {pdfs.map((pdf) => (
          <div
            key={pdf.file_id}
            className={`
              border rounded-lg p-4 cursor-pointer transition-all duration-200
              ${selectedPDF === pdf.file_id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }
            `}
            onClick={() => handleSelectPDF(pdf)}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <FileText className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                  selectedPDF === pdf.file_id ? 'text-blue-600' : 'text-gray-400'
                }`} />
                
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-gray-900 truncate">
                    {pdf.filename}
                  </h4>
                  
                  <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-3 w-3" />
                      <span>{formatDate(pdf.upload_time)}</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Eye className="h-3 w-3" />
                      <span>{pdf.pages} pages</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <Hash className="h-3 w-3" />
                      <span>{pdf.chunks} chunks</span>
                    </div>
                  </div>
                  
                  {selectedPDF === pdf.file_id && (
                    <div className="mt-2 text-xs text-blue-600">
                      ✓ Selected for queries
                    </div>
                  )}
                </div>
              </div>
              
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeletePDF(pdf.file_id, pdf.filename);
                }}
                className="text-gray-400 hover:text-red-500 transition-colors duration-200"
                title="Delete PDF"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {selectedPDF && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-700">
            <strong>Tip:</strong> Questions will now search through the selected PDF content first.
            Click on a PDF again to deselect it.
          </p>
        </div>
      )}
    </div>
  );
};

export default PDFManager;