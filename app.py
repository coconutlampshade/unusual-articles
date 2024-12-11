from flask import Flask, render_template, request, jsonify
import random
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import google.generativeai as genai
from urllib.parse import unquote

app = Flask(__name__)

# Load environment variables and configure Gemini
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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

def generate_blog_post(title, content, url):
    try:
        prompt = f"""
        For this Wikipedia article about {title}, provide:
        1. One compelling sentence explaining why this topic is fascinating
        2. 5-7 key bullet points that would make an engaging story, including:
           - Most surprising facts from the article
           - ONLY direct quotes that appear in the Wikipedia text
           - Historical significance
           - Modern relevance
           - Human interest elements
           - Any controversy or debate
           - Unexpected connections
        
        IMPORTANT: Only use quotes that appear word-for-word in the Wikipedia article text.
        If you can't find good quotes, focus on factual points instead.
        
        Use this content as source: {content[:2000]}
        Format with the hook sentence first, followed by bullet points.
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
        
        return response.text if response.text else None
            
    except Exception as e:
        print(f"\nError generating content for '{title}': {str(e)}")
        return None

@app.route('/')
def home():
    articles = get_random_articles(5)
    article_options = [(get_title_from_url(url), url) for url in articles]
    return render_template('index.html', articles=article_options)

@app.route('/new_articles')
def new_articles():
    articles = get_random_articles(5)
    article_options = [(get_title_from_url(url), url) for url in articles]
    return jsonify(article_options)

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)