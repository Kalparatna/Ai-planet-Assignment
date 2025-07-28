import React from 'react';
import './MathSolutionRenderer.css';

const MathSolutionRenderer = ({ response }) => {
  if (!response || !response.sections) {
    return <div className="math-solution-fallback">{response?.solution || 'No solution available'}</div>;
  }

  const renderContent = (contentItems) => {
    return contentItems.map((item, index) => {
      switch (item.type) {
        case 'formula':
          return (
            <div key={index} className="math-formula">
              <code className="formula-code">{item.content}</code>
            </div>
          );
        
        case 'list_item':
          return (
            <div key={index} className="math-list-item">
              <span className="bullet">•</span>
              <span className="item-content">{item.content}</span>
            </div>
          );
        
        case 'numbered_item':
          return (
            <div key={index} className="math-numbered-item">
              {item.content}
            </div>
          );
        
        default:
          return (
            <p key={index} className="math-text">
              {item.content}
            </p>
          );
      }
    });
  };

  const renderSection = (section, index) => {
    switch (section.type) {
      case 'header':
        return (
          <div key={index} className="math-section math-header-section">
            <h2 className="section-title main-title">{section.title}</h2>
            <div className="section-content">
              {renderContent(section.content)}
            </div>
          </div>
        );
      
      case 'step':
        return (
          <div key={index} className="math-section math-step-section">
            <h3 className="section-title step-title">
              <span className="step-number">Step {index}</span>
              {section.title}
            </h3>
            <div className="section-content step-content">
              {renderContent(section.content)}
            </div>
          </div>
        );
      
      case 'example':
        return (
          <div key={index} className="math-section math-example-section">
            <h4 className="section-title example-title">
              <span className="example-icon">📝</span>
              {section.title}
            </h4>
            <div className="section-content example-content">
              {renderContent(section.content)}
            </div>
          </div>
        );
      
      case 'formula':
        return (
          <div key={index} className="math-section math-formula-section">
            <div className="formula-container">
              {renderContent(section.content)}
            </div>
          </div>
        );
      
      case 'subheader':
        return (
          <div key={index} className="math-section math-subheader-section">
            <h4 className="section-title sub-title">{section.title}</h4>
            <div className="section-content">
              {renderContent(section.content)}
            </div>
          </div>
        );
      
      default:
        return (
          <div key={index} className="math-section math-default-section">
            <div className="section-content">
              {renderContent(section.content)}
            </div>
          </div>
        );
    }
  };

  return (
    <div className="math-solution-container">
      {/* Problem Statement */}
      {response.problem && (
        <div className="math-problem-section">
          <h2 className="problem-title">Problem</h2>
          <div className="problem-content">
            {response.problem}
          </div>
        </div>
      )}
      
      {/* Solution Sections */}
      <div className="math-solution-sections">
        {response.sections.map((section, index) => renderSection(section, index + 1))}
      </div>
    </div>
  );
};

export default MathSolutionRenderer;