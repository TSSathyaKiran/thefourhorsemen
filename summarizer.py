import requests
from bs4 import BeautifulSoup
import re
import nltk
nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def setup_nltk():
    """Setup NLTK and download required resources"""
    try:
        nltk.download('punkt')
        nltk.download('stopwords')

        return True
    except Exception as e:
        print(f"Error setting up NLTK: {str(e)}")
        return False

def get_important_sentences(sentences, num_sentences=10):
    """Extract most important sentences based on keyword frequency"""
    # Combine all sentences into a single string
    text = ' '.join(sentences)
    
    # Tokenize words and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Calculate word frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences based on word frequency
    sentence_scores = {}
    for sentence in sentences:
        score = 0
        words = word_tokenize(sentence.lower())
        for word in words:
            if word in word_freq:
                score += word_freq[word]
        sentence_scores[sentence] = score
    
    # Get top sentences
    important_sentences = sorted(sentence_scores.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:num_sentences]
    
    return [sentence for sentence, score in important_sentences]

def parse_terms_and_conditions(url):
    try:
        setup_nltk()
        # Fetch webpage
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()
        
        # Find terms and conditions section
        potential_sections = []
        
        # Look for relevant sections
        patterns = ['terms', 'conditions', 'tos', 'legal', 'privacy']
        for pattern in patterns:
            # Check IDs and classes
            elements = soup.find_all(['div', 'section', 'article'], 
                                   id=re.compile(pattern, re.I)) + \
                      soup.find_all(['div', 'section', 'article'], 
                                   class_=re.compile(pattern, re.I))
            potential_sections.extend(elements)
        
        # Look for headers
        header_texts = ['Terms of Service', 'Terms and Conditions', 
                       'Terms of Use', 'User Agreement']
        for text in header_texts:
            headers = soup.find_all(string=re.compile(text, re.I))
            for header in headers:
                parent = header.find_parent(['div', 'section', 'article'])
                if parent:
                    potential_sections.append(parent)
        
        # Extract text from sections
        text_content = []
        for section in potential_sections:
            text = section.get_text(separator=' ', strip=True)
            if len(text) > 100:  # Ignore very short sections
                text_content.append(text)
        
        # If no sections found, try main content
        if not text_content:
            main = soup.find('main')
            if main:
                text_content.append(main.get_text(separator=' ', strip=True))
        
        # Clean and split into sentences
        text = ' '.join(text_content)
        text = re.sub(r'\s+', ' ', text)
        sentences = sent_tokenize(text)
        
        # Filter sentences
        filtered_sentences = [
            s for s in sentences
            if len(s) > 30 and  # Remove very short sentences
            not re.search(r'cookie|sign up|login|register', s, re.I)
        ]
        
        # Get most important sentences
        summary = get_important_sentences(filtered_sentences)
        
        return summary
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return ["Error: " + str(e)]  # Print error for debugging

# Call setup_nltk before starting the parsing process
setup_nltk()
