import { useState } from 'react';
import { checkNewsUrl } from '../api';
import type { NewsCheckResult } from '../types';

interface UrlFormProps {
  onResult: (result: NewsCheckResult) => void;
  onLoading: (loading: boolean) => void;
}

const UrlForm = ({ onResult, onLoading }: UrlFormProps) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    onLoading(true);
    setError(null);
    
    try {
      const result = await checkNewsUrl(url);
      console.log('API Response:', result);
      
      // Normalize confidence score to 0-1 range
      let confidenceScore: number;
      if (typeof result.confidence_score === 'number') {
        confidenceScore = Math.min(Math.max(result.confidence_score / 100, 0), 1);
      } else if (typeof result.fake_probability === 'number' && typeof result.real_probability === 'number') {
        confidenceScore = result.is_fake ? 
          Math.min(result.fake_probability / 100, 1) : 
          Math.min(result.real_probability / 100, 1);
      } else {
        confidenceScore = 0.75; 
      }
      
      // Convert API response to the format expected by the UI
      const formattedResult: NewsCheckResult = {
        prediction: result.prediction.toLowerCase() as 'real' | 'fake',
        confidence: confidenceScore,
        explanation: result.credibility_analysis || `Analysis of ${result.analyzed_url}`,
        title: result.title,
        source: result.source,
        date: result.date,
        credibility_analysis: result.credibility_analysis,
        political_bias: result.political_bias,
        bias_score: result.bias_score,
        is_political: result.is_political,
        bias_message: result.bias_message,
        analyzed_url: result.analyzed_url,
        fake_probability: result.fake_probability,
        real_probability: result.real_probability
      };
      
      console.log('Formatted Result:', formattedResult);
      onResult(formattedResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze URL. Please try again.');
      console.error(err);
    } finally {
      onLoading(false);
    }
  };

  return (
    <div className="url-form">
      <h2>Analyze News Article by URL</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter news article URL..."
          required
        />
        {error && <div className="error">{error}</div>}
        <button type="submit">
          {false ? (
            <>
              <div className="spinner" style={{ display: 'inline-block', marginRight: '8px', verticalAlign: 'middle' }}></div>
              Analyzing...
            </>
          ) : (
            'Analyze URL'
          )}
        </button>
      </form>
    </div>
  );
};

export default UrlForm; 