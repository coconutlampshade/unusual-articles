from flask import Flask, render_template, request, jsonify
import random
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import google.generativeai as genai
from urllib.parse import unquote
import time
from functools import lru_cache
from datetime import datetime, timedelta

app = Flask(__name__)

# Load environment variables and configure Gemini
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Rate limiting variables
CALLS_PER_MINUTE = 60  # Adjust based on your API limits
call_timestamps = []

def check_rate_limit():
    """Check if we're within API rate limits"""
    global call_timestamps
    now = datetime.now()
    
    # Remove timestamps older than 1 minute
    call_timestamps = [ts for ts in call_timestamps if now - ts < timedelta(minutes=1)]
    
    if len(call_timestamps) >= CALLS_PER_MINUTE:
        return False
    
    call_timestamps.append(now)
    return True

def get_random_articles(num=5):
    with open('unusual_articles.txt', 'r') as f:
        articles = f.readlines()
    articles = [article.split('. ')[1].strip() for article in articles]
    return random.sample(articles, num)

def get_title_from_url(url):
    # Extract the title from the URL
    title = url.split('/')[-1]
    
    # Fix URL encodings and Unicode
    title = unquote(title, encoding='utf-8')
    
    # Replace underscores with spaces
    title = title.replace('_', ' ')
    
    return title

def fetch_wikipedia_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1', {'id': 'firstHeading'}).text
    content = soup.find('div', {'id': 'mw-content-text'}).get_text()[:2000]
    return title, content, url

@lru_cache(maxsize=1000)
def generate_quick_hook(title, content):
    """Cache hooks to reduce API calls"""
    if not check_rate_limit():
        time.sleep(1)  # Wait if rate limited
        
    try:
        prompt = f"""
        Write ONE fascinating sentence (20-30 words) about this unusual Wikipedia article: '{title}'
        
        Rules:
        - Start with an attention-grabbing fact or detail
        - Use vivid, specific language
        - Focus on the most bizarre, unexpected, or amusing aspect
        - Include numbers, dates, or specific details when relevant
        - Avoid generic phrases like "interesting article" or "fascinating story"
        - End with something that makes the reader want to learn more
        
        Examples of good hooks:
        - "In 1518, hundreds of people in Strasbourg danced themselves to exhaustion and death in a mysterious month-long dancing plague."
        - "Hidden beneath Paris lies 300km of secret tunnels filled with millions of carefully arranged human bones from centuries-old cemeteries."
        
        Content to use: {content[:1000]}
        """
        
        safety_settings = {
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
        }
        
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings
        )
        
        if response and response.text:
            hook = response.text.strip()
            # Validate hook quality
            if len(hook) < 10 or "this article" in hook.lower() or "wikipedia" in hook.lower():
                return f"💡 Discover how {title} became one of history's most unusual stories."
            return hook
        else:
            return f"💡 Discover how {title} became one of history's most unusual stories."
            
    except Exception as e:
        print(f"\nError generating hook for '{title}': {str(e)}")
        return f"💡 Discover how {title} became one of history's most unusual stories."

def get_articles_with_hooks():
    articles = get_random_articles(5)
    article_info = []
    
    for url in articles:
        try:
            title, content, _ = fetch_wikipedia_content(url)
            hook = generate_quick_hook(title, content)
            category = get_article_category(content)
            article_info.append({
                'title': title,
                'url': url,
                'hook': hook,
                'category': category
            })
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue
    
    return article_info

@lru_cache(maxsize=1000)
def get_article_category(content):
    """Cache categories to reduce API calls"""
    if not check_rate_limit():
        time.sleep(1)  # Wait if rate limited
        
    try:
        prompt = f"""
        Based on this content, choose ONE category that best describes this article:
        - Bizarre History
        - Strange Science
        - Unusual Places
        - Weird Culture
        - Peculiar People
        - Odd Objects
        - Mysterious Events
        
        Content: {content[:500]}
        Return ONLY the category name, nothing else.
        """
        
        safety_settings = {
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_ONLY_HIGH",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH"
        }
        
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings
        )
        
        if response and response.text:
            category = response.text.strip()
            # Validate it's one of our categories
            valid_categories = [
                "Bizarre History", "Strange Science", "Unusual Places",
                "Weird Culture", "Peculiar People", "Odd Objects", "Mysterious Events"
            ]
            if category in valid_categories:
                return category
            return "Mysterious Events"  # Default if invalid category returned
        return "Mysterious Events"
            
    except Exception as e:
        print(f"\nError generating category: {str(e)}")
        return "Mysterious Events"

@app.route('/')
def home():
    articles = get_articles_with_hooks()
    return render_template('index.html', articles=articles)

@app.route('/new_articles')
def new_articles():
    articles = get_articles_with_hooks()
    return jsonify(articles)

@app.route('/generate', methods=['POST'])
def generate():
    url = request.form.get('article_url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    try:
        title, content, url = fetch_wikipedia_content(url)
        outline = generate_blog_post(title, content, url)
        
        if outline:
            return jsonify({
                'title': title,
                'content': outline,
                'url': url
            })
        else:
            return jsonify({'error': 'Failed to generate outline'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)