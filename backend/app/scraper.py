import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re

def clean_text(text: str) -> str:
    # Clean the extracted text by removing extra whitespace and special characters
    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?-]', '', text)

    return text.strip()


def extract_article_text(url: str) -> Dict[str, str]:
    # Extract the main text content from a news article URL
    try:
        # Send request with a user agent to avoid being blocked, from a youtube video after I got blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # parse and remove unwanted elements in the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try multiple approaches to find content
        # 1) look for paragraph tags directly
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = ' '.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            if len(text) > 100:  
                return {'text': clean_text(text)}
                
        # 2) try to find the main article content by container classes
        article_containers = soup.find_all(['article', 'main', 'div'], class_=re.compile(r'article|content|post|story|main', re.I))
        if article_containers:
            for container in article_containers:
                text = container.get_text().strip()
                if len(text) > 200:  
                    return {'text': clean_text(text)}
        
        # 3) just get all visible text from the page
        all_text = soup.get_text().strip()
        if len(all_text) > 500:
            return {'text': clean_text(all_text)}
            
        return {'error': 'No text content could be extracted from the article'}
        
    except requests.RequestException as e:
        return {'error': f'Failed to fetch the article: {str(e)}'}
    except Exception as e:
        return {'error': f'Error processing the article: {str(e)}' }

if __name__ == "__main__":
    # Test the scraper with a sample URL
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence" 
    result = extract_article_text(test_url)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        exit(1)
    else:
        print("Successfully extracted article text:")
        print("\nFirst 500 characters:")
        print(result['text'][:500])
        print(f"\nTotal length: {len(result['text'])} characters")
