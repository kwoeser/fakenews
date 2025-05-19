import pandas as pd
import joblib
import json
import os
import re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score

def clean_text(text: str) -> str:
    # Clean the article text by removing common patterns and noise.
    if not isinstance(text, str):
        return ""
        
    text = text.lower()
    
    # Remove Reuters attribution and similar patterns, I saw someone on kaggle talk about how this improved their model
    patterns_to_remove = [
        r'\(reuters\)',
        r'reuters\s*[-–—]\s*',
        r'by\s+reuters',
        r'\(ap\)',
        r'associated\s+press\s*[-–—]\s*',
        r'by\s+associated\s+press',
        r'\(bloomberg\)',
        r'bloomberg\s*[-–—]\s*',
        r'by\s+bloomberg',
        r'\(cnn\)',
        r'cnn\s*[-–—]\s*',
        r'by\s+cnn',
        r'\(bbc\)',
        r'bbc\s*[-–—]\s*',
        r'by\s+bbc',
        r'\(afp\)',
        r'agence\s+france\s+presse\s*[-–—]\s*',
        r'by\s+afp',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove URLs, email addresses, and special characters
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def train_fake_news_model(true_path="datasets/True.csv", fake_path="datasets/Fake.csv"):
    # Create models directory if it doesn't exist
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    true_df = pd.read_csv(true_path)
    fake_df = pd.read_csv(fake_path)
    
    # cleaning dataseet and add labels
    true_df['label'] = 'REAL'
    fake_df['label'] = 'FAKE'
    
    df = pd.concat([true_df, fake_df], ignore_index=True)
    df = df.dropna(subset=['text'])
    
    print("Cleaning article texts...")
    df['text'] = df['text'].apply(clean_text)
    
    # need to remove empty texts after cleaning
    df = df[df['text'].str.len() > 0]
    X = df['text']
    y = df['label'].map({'FAKE': 0, 'REAL': 1})

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Pipeline: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            stop_words='english',
            max_df=0.7,
            min_df=5, 
            ngram_range=(1, 2)  
        )),
        ('clf', LogisticRegression(max_iter=1000)),
    ])

    print("Training model...")
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    
    metrics = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'model_type': 'LogisticRegression',
        'vectorizer': 'TfidfVectorizer',
        'dataset_stats': {
            'total_samples': len(df),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'fake_samples': len(fake_df),
            'real_samples': len(true_df)
        },
        'model_parameters': {
            'max_iter': 1000,
            'max_df': 0.7,
            'min_df': 5,
            'ngram_range': (1, 2),
            'stop_words': 'english'
        },
        'performance_metrics': {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        },
        'detailed_classification_report': classification_report(y_test, y_pred, output_dict=True)
    }

    # Save metrics to JSON file in models directory
    metrics_file = os.path.join(models_dir, 'model_metrics.json')
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Training metrics saved to {metrics_file}")

    # Save model to models directory
    model_file = os.path.join(models_dir, 'fake_news_model.pkl')
    joblib.dump(pipeline, model_file)
    print(f"Model trained and saved as {model_file}")

if __name__ == "__main__":
    train_fake_news_model()
