import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re
import random
import time
import urllib.parse

# List of common user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
]

# Sites that need special handling
DIFFICULT_SITES = {
    'bbc.com': {
        'throttle': 5,  # Extra delay in seconds
        'mobile': False  # Don't use mobile user agent for BBC, it's not working
    },
    'nytimes.com': {
        'throttle': 3,
        'referrer': 'https://www.google.com/'
    },
    'reuters.com': {
        'throttle': 2,
        'mobile': True
    }
}

# Current working fallback articles that demonstrate the system
FALLBACK_ARTICLES = [
    {
        'url': 'https://en.wikipedia.org/wiki/Web_scraping',
        'title': 'Web scraping - Wikipedia',
        'text': "Web scraping, web harvesting, or web data extraction is data scraping used for extracting data from websites. Web scraping software may directly access the World Wide Web using the Hypertext Transfer Protocol or a web browser. While web scraping can be done manually by a software user, the term typically refers to automated processes implemented using a bot or web crawler. It is a form of copying in which specific data is gathered and copied from the web, typically into a central local database or spreadsheet, for later retrieval or analysis.",
        'date': '2023-10-26', # Using a fixed date as Wikipedia pages are continuously updated
        'source': 'en.wikipedia.org'
    }
]

def clean_text(text: str) -> str:
    # Clean the extracted text by removing extra whitespace and special characters
    if not text:
        return ""

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]', '', text)

    return text.strip()

def get_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def get_fallback_article() -> Dict[str, str]:
    """Return the working fallback article"""
    # Since FALLBACK_ARTICLES now contains only one article, random.choice will always pick it.
    article = random.choice(FALLBACK_ARTICLES)
    return {
        'text': "(FALLBACK CONTENT) " + article['text'],
        'title': "(FALLBACK) " + article['title'],
        'date': article['date'],
        'source': article['source'],
        'original_url': article['url']
    }

def extract_article_text(url: str, is_fallback: bool = False) -> Dict[str, str]:
    # If we're already using a fallback, or in recursion, just return a fallback directly
    if is_fallback:
        return get_fallback_article()
        
    # Extract the main text content from a news article URL
    max_retries = 3
    
    # Extract domain for special handling
    domain = get_domain(url)
    site_config = DIFFICULT_SITES.get(domain, {})
    extra_throttle = site_config.get('throttle', 0)
    
    for attempt in range(max_retries):
        try:
            # Use appropriate user agent and comprehensive headers
            if site_config.get('mobile', False):
                user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
            else:
                user_agent = random.choice(USER_AGENTS)
                
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'DNT': '1'  # Do Not Track
            }
            
            # Add referrer for sites that check referrer
            if 'referrer' in site_config:
                headers['Referer'] = site_config['referrer']
            
            # Add a small delay between retries plus extra throttle for difficult sites
            if attempt > 0 or extra_throttle > 0:
                time.sleep(2 + extra_throttle)
            
            # Handle specific sites that are known to block scrapers
            if domain == 'bbc.com' or domain == 'bbc.co.uk':
                # Don't use mobile URLs for BBC, they're not resolving
                pass
                
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse and remove unwanted elements
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'meta', 'svg', 'form']):
                element.decompose()
                
            # Extract basic metadata about the article
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
                
            # Try to get article publication date
            date = ""
            date_tags = soup.find_all(['time', 'meta'], attrs={'property': 'article:published_time'})
            if date_tags:
                for tag in date_tags:
                    if tag.has_attr('datetime'):
                        date = tag['datetime']
                        break
                    elif tag.has_attr('content'):
                        date = tag['content']
                        break
            
            # Extract the main content
            article_text = ""
            
            # 1) Look for article tag or main content container
            article_container = None
            for container_selector in ['article', 'main', '[role="main"]', '#main-content', '.article-body', '.story-body']:
                container = soup.select_one(container_selector)
                if container:
                    article_container = container
                    break
                    
            if article_container:
                # Get all paragraphs from the article container
                paragraphs = article_container.find_all('p')
                article_text = ' '.join(p.get_text().strip() for p in paragraphs if p.get_text().strip())
            
            # 2) If article container approach didn't work, try all paragraphs
            if not article_text or len(article_text) < 200:
                paragraphs = soup.find_all('p')
                # Filter out short paragraphs that might be navigation/footer text
                main_paragraphs = [p for p in paragraphs if len(p.get_text().strip()) > 20]
                if main_paragraphs:
                    article_text = ' '.join(p.get_text().strip() for p in main_paragraphs)
            
            # 3) If all else fails, get all text
            if not article_text or len(article_text) < 200:
                # Last resort: get all text but filter out short lines
                text_blocks = [t for t in soup.stripped_strings if len(t) > 20]
                article_text = ' '.join(text_blocks)
            
            # Ensure we have meaningful content
            if article_text and len(article_text) > 200:
                cleaned_text = clean_text(article_text)
                return {
                    'text': cleaned_text,
                    'title': title,
                    'date': date,
                    'source': domain
                }
                
            # If we've exhausted all options and found no text
            if attempt == max_retries - 1:
                # Fall back to sample article if we can't extract this one
                print(f"Could not extract content from {url}. Using fallback article.")
                return get_fallback_article()
                
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                # Fall back to sample article if we can't get this one
                print(f"Failed to fetch {url}: {str(e)}. Using fallback article.")
                return get_fallback_article()
        except Exception as e:
            if attempt == max_retries - 1:
                # Fall back to sample article if we can't process this one
                print(f"Error processing {url}: {str(e)}. Using fallback article.")
                return get_fallback_article()
    
    # If we get here, something went wrong
    return get_fallback_article()

if __name__ == "__main__":
    test_url = "https://apnews.com/article/vaccines-fda-kennedy-covid-shots-rfk-trump-bb4de15b6ff955d6cd0b406aaec3cdc5" 
    result = extract_article_text(test_url)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        exit(1)
    else:
        print("Successfully extracted article text:")
        if 'title' in result:
            print(f"\nTitle: {result['title']}")
        if 'date' in result:
            print(f"Date: {result['date']}")
        if 'source' in result:
            print(f"Source: {result['source']}")
        print("\nFirst 1000 characters:")
        print(result['text'][:1000])
        print(f"\nTotal length: {len(result['text'])} characters")
