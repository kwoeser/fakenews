export interface NewsCheckResult {
  prediction: 'real' | 'fake' | 'REAL' | 'FAKE';
  confidence: number;
  explanation?: string;
  title?: string;
  source?: string;
  date?: string;
  credibility_analysis?: string;
  political_bias?: string;
  bias_score?: number;
  is_political?: boolean;
  bias_message?: string;
  analyzed_url?: string;
}

export interface NewsCheckRequest {
  text: string;
} 