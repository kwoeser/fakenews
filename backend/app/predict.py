import joblib
from typing import Dict, Union, List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

# Create a thread pool for CPU-bound tasks
thread_pool = ThreadPoolExecutor(max_workers=4)

class ModelPredictor:
    def __init__(self, model_path = 'models/fake_news_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.load_lock = asyncio.Lock()

    async def load_model(self):
        # Asynchronously load the model if it's not already loaded and check twice to avoid race condition
        if self.model is None:
            async with self.load_lock:
                if self.model is None: 
                    try:
                        # Run model loading in thread pool since it's CPU-bound
                        self.model = await asyncio.get_event_loop().run_in_executor(
                            thread_pool,
                            joblib.load,
                            self.model_path
                        )
                    except Exception as e:
                        raise Exception(f"Failed to load model from {self.model_path}: {str(e)}")
        return self.model


    async def predict_article(self, article_text: str):
        # Asynchronously predict whether an article is fake news and return the confidence score
        try:
            model = await self.load_model()
            
            # Run prediction in thread pool 
            probabilities = await asyncio.get_event_loop().run_in_executor(
                thread_pool,
                lambda: model.predict_proba([article_text])[0]
            )
            
            fake_prob = min(probabilities[0] * 100, 100)
            real_prob = min(probabilities[1] * 100, 100)
            
            is_fake = fake_prob > real_prob
            confidence_score = fake_prob if is_fake else real_prob
            confidence_score = min(confidence_score, 100)
            
            return {
                'prediction': 'FAKE' if is_fake else 'REAL',
                'confidence_score': round(confidence_score, 2),
                'is_fake': is_fake,
                'fake_probability': round(fake_prob, 2),
                'real_probability': round(real_prob, 2)
            }
        except Exception as e:
            return {
                'error': f'Error making prediction: {str(e)}'
            }

    async def predict_batch(self, articles: List[str]):
        # Asynchronously predict multiple articles in parallel
        tasks = [self.predict_article(article) for article in articles]
        return await asyncio.gather(*tasks)


predictor = ModelPredictor()
async def predict_article(article_text: str):
    return await predictor.predict_article(article_text)

async def predict_batch(articles: List[str]):
    return await predictor.predict_batch(articles)

if __name__ == "__main__":
    async def main():
        test_articles = [
            "https://apnews.com/article/vaccines-fda-kennedy-covid-shots-rfk-trump-bb4de15b6ff955d6cd0b406aaec3cdc5",
            "Another article to test batch prediction."
        ]
        
        # Test single prediction
        result = await predict_article(test_articles[0])
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print("\nSingle Prediction Result:")
            print(f"Article is predicted to be: {result['prediction']}")
            print(f"Confidence Score: {result['confidence_score']}%")
            print(f"Fake Probability: {result['fake_probability']}%")
            print(f"Real Probability: {result['real_probability']}%")
        
        # Test batch prediction
        results = await predict_batch(test_articles)
        print("\nBatch Prediction Results:")
        for i, result in enumerate(results, 1):
            print(f"\nArticle {i}:")
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Prediction: {result['prediction']}")
                print(f"Confidence Score: {result['confidence_score']}%")

    asyncio.run(main())
    