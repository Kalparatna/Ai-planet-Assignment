import React, { useState } from 'react';
import { Upload, FileText, Search } from './Icons';
import PDFUpload from './PDFUpload';
import PDFManager from './PDFManager';

const PDFTab = ({ onPDFSelect, selectedPDF }) => {
  const [activeSubTab, setActiveSubTab] = useState('upload');
  const [uploadKey, setUploadKey] = useState(0); // Force re-render of upload component

  const handleUploadSuccess = (result) => {
    // Switch to manager tab after successful upload
    setActiveSubTab('manage');
    // Force refresh of upload component
    setUploadKey(prev => prev + 1);
  };

  const handleUploadError = (error) => {
    console.error('Upload error:', error);
  };

  const subTabs = [
    {
      id: 'upload',
      label: 'Upload PDF',
      icon: Upload,
      description: 'Upload mathematical documents'
    },
    {
      id: 'manage',
      label: 'Manage PDFs',
      icon: FileText,
      description: 'View and manage uploaded PDFs'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Sub-tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {subTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`
                  group inline-flex items-center py-2 px-1 border-b-2 font-medium text-sm
                  ${activeSubTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className={`
                  -ml-0.5 mr-2 h-5 w-5
                  ${activeSubTab === tab.id
                    ? 'text-blue-500'
                    : 'text-gray-400 group-hover:text-gray-500'
                  }
                `} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Sub-tab Content */}
      <div className="min-h-[400px]">
        {activeSubTab === 'upload' && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Upload Mathematical Documents
              </h3>
              <p className="text-gray-600 mb-6">
                Upload PDF files containing mathematical content, textbooks, notes, or problem sets.
                The system will extract and index the content for intelligent querying.
              </p>
            </div>

            <PDFUpload
              key={uploadKey}
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">How it works:</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Upload PDF files with mathematical content</li>
                <li>• Text is extracted and intelligently chunked</li>
                <li>• Content is indexed in a vector database</li>
                <li>• Ask questions and get answers from your documents</li>
                <li>• Integrated with the main math routing system</li>
              </ul>
            </div>
          </div>
        )}

        {activeSubTab === 'manage' && (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Manage Your Documents
              </h3>
              <p className="text-gray-600 mb-6">
                View, select, and manage your uploaded PDF documents.
                Select a PDF to prioritize it in query responses.
              </p>
            </div>

            <PDFManager onPDFSelect={onPDFSelect} />

            {selectedPDF && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <Search className="h-5 w-5 text-green-600" />
                  <div>
                    <h4 className="font-medium text-green-900">
                      PDF Selected: {selectedPDF.filename}
                    </h4>
                    <p className="text-sm text-green-700">
                      Questions will search this document first before checking other sources.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default PDFTab;