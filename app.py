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

def generate_quick_hook(title, content):
    try:
        prompt = f"""
        Write ONE short, compelling sentence (20-30 words) explaining why this Wikipedia article about '{title}' is fascinating and unusual.
        Use this content: {content[:1000]}
        Focus on the most surprising or unusual aspect.
        """
        
        response = model.generate_content(prompt)
        return response.text if response.text else None
            
    except Exception as e:
        print(f"\nError generating hook for '{title}': {str(e)}")
        return None

def get_articles_with_hooks():
    articles = get_random_articles(5)
    article_info = []
    
    for url in articles:
        try:
            title, content, _ = fetch_wikipedia_content(url)
            hook = generate_quick_hook(title, content)
            article_info.append({
                'title': title,
                'url': url,
                'hook': hook
            })
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            continue
    
    return article_info

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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)