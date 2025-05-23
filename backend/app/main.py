import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from .predict import predict_article
from .scraper import extract_article_text
from .bias_detector import detect_political_bias
from typing import Optional, Dict, Union
import re

# I SHOULD'VE JUST USED A PRETRAINED MODEL 
app = FastAPI(
    title="Fake News Detection API",
    description="API for detecting fake news articles",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend domain in production TODO!!!!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ArticleRequest(BaseModel):
    text: Optional[str] = Field(None, min_length=50, description="The article text to analyze")
    url: Optional[str] = Field(None, description="Optional URL of the article")

    @model_validator(mode='after')
    def check_text_or_url(self):
        # Ensure either text or url is provided.
        if not self.text and not self.url:
            raise ValueError('Either text or url must be provided')
        return self

class PredictionResponse(BaseModel):
    prediction: str
    confidence_score: float
    is_fake: bool
    fake_probability: float
    real_probability: float

class AnalyzeUrlResponse(PredictionResponse):
    analyzed_url: str
    title: Optional[str] = None
    source: Optional[str] = None
    date: Optional[str] = None
    credibility_analysis: Optional[str] = None
    political_bias: Optional[str] = None
    bias_score: Optional[float] = None
    is_political: Optional[bool] = None
    bias_message: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Fake News Detection API",
        "endpoints": {
            "/predict": "POST - Analyze article text for fake news",
            "/analyze-url": "POST - Analyze URL for fake news",
            "/docs": "GET - API documentation",
        }
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: ArticleRequest):
    # Predict whether an article is fake news. Takes article text and returns prediction results with confidence scores.
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Article text is required")
            
        result = await predict_article(request.text)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-url", response_model=AnalyzeUrlResponse)
async def analyze_url(request: ArticleRequest):
    # Analyze a URL for fake news by scraping the content and running it through the prediction model.
    if not request.url:
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Scrape article text
    scraped_data = extract_article_text(request.url)
    
    if 'error' in scraped_data:
        raise HTTPException(status_code=400, detail=f"Failed to scrape URL: {scraped_data['error']}")
    
    if not scraped_data.get('text'):
        raise HTTPException(status_code=400, detail="No text content could be extracted from the URL.")

    # Get prediction result for the scraped text
    prediction_result = await predict_article(scraped_data['text'])
    
    if 'error' in prediction_result:
        raise HTTPException(status_code=500, detail=f"Error making prediction: {prediction_result['error']}")
    
    # Add credibility analysis based on the prediction
    credibility_analysis = ""
    if prediction_result['is_fake']:
        fake_probability = prediction_result['fake_probability']
        if fake_probability > 90:
            credibility_analysis = "This article contains multiple red flags indicating it is highly likely to be fake news."
        elif fake_probability > 70:
            credibility_analysis = "This article shows significant patterns common in fake news sources."
        else:
            credibility_analysis = "This article has some characteristics of misinformation, suggesting caution is warranted."
    else:
        real_probability = prediction_result['real_probability']
        if real_probability > 90:
            credibility_analysis = "This article demonstrates strong credibility patterns typical of reliable news sources."
        elif real_probability > 70:
            credibility_analysis = "This article appears to be generally credible, with patterns consistent with legitimate reporting."
        else:
            credibility_analysis = "While this article appears more credible than not, some verification with additional sources is recommended."
    
    # Detect political bias
    bias_data = detect_political_bias(scraped_data['text'])
            
    return AnalyzeUrlResponse(
        analyzed_url=request.url,
        title=scraped_data.get('title', ''),
        source=scraped_data.get('source', ''),
        date=scraped_data.get('date', ''),
        credibility_analysis=credibility_analysis,
        political_bias=bias_data['bias'],
        bias_score=bias_data.get('bias_score', 0),
        is_political=bias_data.get('is_political', False),
        bias_message=bias_data.get('message', ''),
        **prediction_result
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
