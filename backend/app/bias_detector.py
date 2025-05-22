import re

# Define political bias indicators, could be improved and might be bias cuz of me. ALSO THIS IS VERY AMERICAN CENTRIC
LEFT_LEANING_TERMS = [
    'progressive', 'liberal', 'democrat', 'socialism', 'communism', 'social justice',
    'climate change', 'universal healthcare', 'gun control', 'inequality',
    'diversity', 'reproductive rights', 'green new deal', 'regulation',
    'welfare', 'labor union', 'immigration rights', 'black lives matter',
    'systemic racism', 'privilege', 'defund police', 'gender equality', 'pro-choice',
]

RIGHT_LEANING_TERMS = [
    'conservative', 'republican', 'patriot', 'tradition', 'family values',
    'america first', 'second amendment', 'pro-life', 'free market', 
    'small government', 'deregulation', 'tax cuts', 'religious freedom',
    'national security', 'border security', 'law and order', 'constitutional',
    'fiscal responsibility', 'blue lives matter', 'pro-gun', 'pro-police', 'pro-life',
    'pro-trump', 'MAGA', 'Make America Great Again'
]

# Terms that indicate content is political in nature
POLITICAL_TOPIC_INDICATORS = [
    'politics', 'election', 'vote', 'president', 'congress', 'senate', 'house of representatives',
    'government', 'policy', 'legislation', 'administration', 'campaign', 'ballot', 'democracy', 
    'republican', 'democrat', 'liberal', 'conservative', 'party', 'left wing', 'right wing',
    'politician', 'political', 'legislative', 'bill', 'law', 'amendment', 'constitution',
    'cabinet', 'parliament', 'prime minister', 'governor', 'senator', 'representative',
    'supreme court', 'justice department', 'federal', 'state', 'national', 'international',
    'treaty', 'foreign policy', 'domestic policy', 'regulation', 'deregulation', 'budget',
    'deficit', 'taxes', 'spending', 'social security', 'medicare', 'medicaid', 'healthcare',
    'obamacare', 'immigration', 'border', 'climate change', 'environment', 'fossil fuels',
    'renewable energy', 'abortion', 'gun control', 'second amendment', 'war', 'military',
    'defense', 'terrorism', 'protest', 'rally', 'debate', 'white house'
]



"""
very simple bias detector that uses a list of left and right leaning terms to detect bias.
it's not good at all

Problems
---------
1) When the text says conservative it always detects it as right leaning, even if it's not
2) It's very american centric, but thats fine idc bout other places.
3) It's not good at detecting far left leaning bias
4) it detects far right leaning bias even if the text seems more center right or middle right


"""



def is_political_content(text: str) -> bool:
    # Determine if the content is political in nature
    text_lower = text.lower()
    
    political_term_count = 0
    for term in POLITICAL_TOPIC_INDICATORS:
        pattern = r'\b' + re.escape(term) + r'\b'
        political_term_count += len(re.findall(pattern, text_lower))
    
    word_count = len(text_lower.split())
    if word_count == 0:
        return False
        
    political_term_density = (political_term_count * 1000) / word_count
    
    # determine if content is political
    return political_term_count >= 3 or political_term_density >= 5

def detect_political_bias(text: str):
    # Detect political bias in the text based on keyword analysis
    text_lower = text.lower()
    
    # First check if the content is political in nature
    is_political = is_political_content(text)
    
    if not is_political:
        return {
            "is_political": False,
            "bias": "Not Political Content",
            "bias_score": 0,
            "message": "This content doesn't appear to be political in nature, so political bias analysis is not applicable."
        }
    
    # Count occurrences of politically charged terms
    left_count = 0
    for term in LEFT_LEANING_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        left_count += len(re.findall(pattern, text_lower))
    
    right_count = 0
    for term in RIGHT_LEANING_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        right_count += len(re.findall(pattern, text_lower))
    
    # Determine bias based on counts
    total_count = left_count + right_count
    if total_count == 0:
        return {
            "is_political": True,
            "bias": "Neutral/Balanced",
            "bias_score": 0,
            "left_term_count": 0,
            "right_term_count": 0,
            "message": "While this appears to be political content, no clear bias was detected."
        }
    
    left_percentage = (left_count / total_count) * 100
    right_percentage = (right_count / total_count) * 100
    
    # Calculate bias score (-100 to 100, negative is left, positive is right)
    bias_score = ((right_count - left_count) / total_count) * 100
    
    if bias_score < -30:
        bias = "Strongly Left-Leaning"
        message = "This content shows a strong left-leaning political bias."
    elif bias_score < -10:
        bias = "Moderately Left-Leaning"
        message = "This content shows a moderate left-leaning political bias."
    elif bias_score < 10:
        bias = "Neutral/Balanced"
        message = "This content appears to present a relatively balanced political perspective."
    elif bias_score < 30:
        bias = "Moderately Right-Leaning"
        message = "This content shows a moderate right-leaning political bias."
    else:
        bias = "Strongly Right-Leaning"
        message = "This content shows a strong right-leaning political bias."
    
    return {
        "is_political": True,
        "bias": bias,
        "bias_score": round(bias_score, 1),
        "left_term_count": left_count,
        "right_term_count": right_count,
        "message": message
    }