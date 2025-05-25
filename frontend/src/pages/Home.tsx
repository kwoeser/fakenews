import { useState, useEffect } from 'react';
import { Sun, Moon } from 'lucide-react';
import UrlForm from '../components/UrlForm';
import ResultDisplay from '../components/ResultDisplay';
import type { NewsCheckResult } from '../types';

const Home = () => {
  const [result, setResult] = useState<NewsCheckResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <div className={`home-page ${theme}`}>
      <nav className="navbar">
        <div className="navbar-logo">
          <img src="/logo.png" alt="Logo" />
        </div>
        <div className="navbar-links">
          <button onClick={toggleTheme} className="theme-toggle-button">
            {theme === 'light' ? <Moon size={24} /> : <Sun size={24} />}
          </button>
          <a href="https://github.com/kwoeser/fakenews" target="_blank" rel="noopener noreferrer">
            {/* SVG for github icon */}
            <svg height="24" width="24" viewBox="0 0 16 16" fill="currentColor">
              <path fillRule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
            </svg>
          </a>
        </div>
      </nav>

      <div className="title-section">
        <div className="title-row">
          <h1>Fake News Detector</h1>
        </div>
      </div>

      <p className="explanation-text">
        <strong>Each article you submit is analyzed using AI to detect patterns 
        common in fake news, providing you with a credibility assessment to help 
        navigate today's complex information landscape. The model was trained on a dataset 
        with 10000+ articles. This is a work in progress and has many biases and issues.</strong>
      </p>
      
      {/* URL form */}
      <main>
        <div className="tab-container">
          {/* <div className="tab-content"> */}
            <UrlForm onResult={(res) => { setResult(res); setIsLoading(false); }} onLoading={setIsLoading} />
          {/* </div> */}
        </div>
        
        {isLoading && (
          <div className="spinner-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
            <div className="spinner" />
          </div>
        )}
        {!isLoading && result && <ResultDisplay result={result} />}
      </main>
      
      <footer>
        <p>This tool uses AI to analyze text patterns. Results should be verified with additional sources.</p>
      </footer>
    </div>
  );
};

export default Home; 