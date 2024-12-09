import random
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

# Load environment variables first
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("No API key found. Make sure you have a .env file with GOOGLE_API_KEY=your-key")

# Import and configure Gemini with some delay to avoid initialization issues
time.sleep(1)  # Small delay before importing
import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_random_article():
    with open('unusual_articles.txt', 'r') as f:
        articles = f.readlines()
    # Remove index number and newline, get just the URL
    articles = [article.split('. ')[1].strip() for article in articles]
    return random.choice(articles)

def fetch_wikipedia_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Get the main content
    content = soup.find('div', {'id': 'mw-content-text'})
    
    # Get article title
    title = soup.find('h1', {'id': 'firstHeading'}).text
    
    # Extract text and references
    paragraphs = content.find_all('p')
    text = '\n'.join([p.get_text() for p in paragraphs])
    
    return title, text, url

def generate_blog_post(title, content, url):
    prompt = f"""
    Write a 300-word blog post about {title}. 
    Use this Wikipedia content as your source: {content[:2000]}...
    
    Requirements:
    1. Include at least 2 direct quotes from the Wikipedia article
    2. Include the Wikipedia URL as a reference
    3. Make it engaging and interesting for general readers
    4. Keep it to approximately 300 words
    5. Format in markdown with proper headings and links
    6. Include an SEO-friendly title
    7. Write it in the style of Mental Floss and Atlas Obscura
    8. Include the best and most interesting facts from the article
    9. Use humor and wit where appropriate
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    # Get random article
    article_url = get_random_article()
    print(f"Selected article: {article_url}")
    
    # Fetch content
    title, content, url = fetch_wikipedia_content(article_url)
    print(f"Generating blog post about: {title}")
    
    # Generate and save blog post
    blog_post = generate_blog_post(title, content, url)
    
    # Save to file with title as filename
    filename = f"blog_posts/{title.lower().replace(' ', '_')}.md"
    os.makedirs('blog_posts', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(blog_post)
    
    print(f"Blog post saved to: {filename}")
    print("\nBlog post content:")
    print("=" * 50)
    print(blog_post)

if __name__ == "__main__":
    main()
