import type { NewsCheckResult } from '../types';

interface ResultDisplayProps {
  result: NewsCheckResult | null;
}

const ResultDisplay = ({ result }: ResultDisplayProps) => {
  if (!result) return null;

  const { 
    prediction, 
    confidence, 
    explanation, 
    title, 
    source, 
    date, 
    analyzed_url, 
    political_bias, 
    bias_score,
    is_political,
    bias_message
  } = result;
  
  // Ensure confidence is displayed correctly as percentage between 0-100
  const confidencePercent = typeof confidence === 'number' && !isNaN(confidence) 
    ? Math.min(Math.round(confidence * 100), 100) 
    : 0;

  // Format date if available
  const formattedDate = date ? new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }) : null;

  // Get bias class for styling
  const getBiasClass = () => {
    if (!political_bias) return '';
    
    const bias = political_bias.toLowerCase();
    if (bias.includes('not political')) return 'not-political';
    if (bias.includes('strongly left')) return 'strongly-left';
    if (bias.includes('moderately left')) return 'moderately-left';
    if (bias.includes('neutral')) return 'neutral-bias';
    if (bias.includes('moderately right')) return 'moderately-right';
    if (bias.includes('strongly right')) return 'strongly-right';
    return '';
  };

  // Check if content is non-political
  const isNonPolitical = is_political === false || (political_bias && political_bias.toLowerCase().includes('not political'));

  return (
    <div className={`result-display ${prediction.toLowerCase()}`}>
      <h2>Analysis Results</h2>
      <div className="result-content">
        {title && (
          <div className="article-title">
            <h3>{title}</h3>
            {source && <p className="article-source">Source: {source}</p>}
            {formattedDate && <p className="article-date">Published: {formattedDate}</p>}
          </div>
        )}
        
        <div className="result-header">
          <span className="prediction">
            {prediction.toLowerCase() === 'fake' ? '⚠️ Likely Misinformation' : '✓ Likely Factual'}
          </span>
          <span className="confidence">
            Confidence: {confidencePercent}%
          </span>
        </div>
        
        {explanation && (
          <div className="explanation">
            <h3>Credibility Analysis</h3>
            <p>{explanation}</p>
          </div>
        )}
        
        {political_bias && (
          <div className="political-bias">
            <h3>Political Bias Analysis</h3>
            {isNonPolitical ? (
              <div className="non-political-content">
                <p>{bias_message || "This content doesn't appear to be political in nature, so political bias analysis is not applicable."}</p>
              </div>
            ) : (
              <div className="bias-container">
                <div className="bias-scale">
                  <div className="bias-labels">
                    <span>Left</span>
                    <span>Center</span>
                    <span>Right</span>
                  </div>
                  <div className="bias-bar">
                    <div 
                      className="bias-indicator"
                      style={{ 
                        left: `${bias_score && !isNaN(bias_score) ? Math.min(Math.max((bias_score + 100) / 2, 0), 100) : 50}%` 
                      }}
                    ></div>
                  </div>
                </div>
                <div className={`bias-result ${getBiasClass()}`}>
                  {political_bias}
                </div>
                {bias_message && <p className="bias-explanation">{bias_message}</p>}
              </div>
            )}
          </div>
        )}
        
        {analyzed_url && (
          <div className="analyzed-url">
            <h3>Analyzed URL</h3>
            <a href={analyzed_url} target="_blank" rel="noopener noreferrer" className="url-link">
              {analyzed_url}
            </a>
          </div>
        )}
        
        <div className="disclaimer">
          <p>This is an automated assessment based on text pattern analysis. 
          Always verify information with trusted sources before drawing conclusions.</p>
        </div>
      </div>
    </div>
  );
};

export default ResultDisplay; 