from flask import Flask, render_template, request, jsonify
from pick_and_write import get_random_articles, fetch_wikipedia_content, generate_blog_post
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

@app.route('/')
def home():
    articles = get_random_articles(5)
    # Convert URLs to titles for display
    article_options = [(url.split('/')[-1].replace('_', ' '), url) for url in articles]
    return render_template('index.html', articles=article_options)

@app.route('/new_articles')
def new_articles():
    articles = get_random_articles(5)
    article_options = [(url.split('/')[-1].replace('_', ' '), url) for url in articles]
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
    app.run(debug=True)