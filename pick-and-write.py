import random
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
import logging
import warnings

# Load environment variables first
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    raise ValueError("No API key found. Make sure you have a .env file with GOOGLE_API_KEY=your-key")

# Suppress warnings
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)

# Import and configure Gemini with some delay to avoid initialization issues
time.sleep(1)  # Small delay before importing
import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def get_random_articles(num=5):
    with open('unusual_articles.txt', 'r') as f:
        articles = f.readlines()
    # Remove index number and newline, get just the URL
    articles = [article.split('. ')[1].strip() for article in articles]
    return random.sample(articles, num)

def get_title_from_url(url):
    # Extract the title from the URL
    title = url.split('/')[-1]
    
    # Fix common URL encodings
    title = title.replace('%27', "'")  # Fix apostrophes
    title = title.replace('%28', '(')  # Fix parentheses
    title = title.replace('%29', ')')
    title = title.replace('%2C', ',')  # Fix commas
    title = title.replace('%22', '"')  # Fix quotes
    title = title.replace('_', ' ')    # Replace underscores with spaces
    
    return title

def select_and_generate_articles():
    while True:  # Keep going until user quits
        articles = get_random_articles(5)
        remaining_articles = articles.copy()
        
        while remaining_articles:
            print("\nHere are the remaining articles. Please select one (1-5) or press 's' for new options:")
            for idx, url in enumerate(remaining_articles, 1):
                title = get_title_from_url(url)
                print(f"{idx}. {title}")
                print(f"   {url}\n")
            
            choice = input("Enter your choice (1-5), 's' to skip, or 'q' to quit: ").lower()
            
            if choice == 's':
                break  # Break inner loop to get new articles
            
            if choice == 'q':
                return  # Exit the function entirely
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(remaining_articles):
                    selected_url = remaining_articles[choice_num - 1]
                    print(f"\nSelected article: {selected_url}")
                    
                    # Fetch and generate content
                    title, content, url = fetch_wikipedia_content(selected_url)
                    print(f"Generating outline for: {title}")
                    
                    blog_post = generate_blog_post(title, content, url)
                    if blog_post:
                        print("\nOutline:")
                        print("=" * 50)
                        print(blog_post)
                        print("=" * 50)
                    # Remove the selected article from the list
                    remaining_articles.pop(choice_num - 1)
                    
                    if remaining_articles:
                        continue_choice = input("\nWould you like to generate an outline for another article? (y/n): ").lower()
                        if continue_choice != 'y':
                            print("\nHere are 5 new random articles...")
                            break  # Break inner loop to get new articles
                    
                else:
                    print(f"Please enter a number between 1 and {len(remaining_articles)} (or 's' to skip, 'q' to quit)")
            except ValueError:
                if choice not in ['s', 'q']:
                    print("Please enter a valid number, 's' to skip, or 'q' to quit")

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
    try:
        prompt = f"""
        For this Wikipedia article about {title}, provide:
        1. One compelling sentence explaining why this topic is fascinating
        2. 5-7 key bullet points that would make an engaging story, including:
           - Most surprising facts from the article
           - ONLY direct quotes that appear in the Wikipedia text (do not make up or modify quotes)
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
        
        if not response.text:
            print(f"\nWarning: Content generation failed for '{title}'.")
            print("Please select a different article.")
            return None
            
        return response.text
        
    except Exception as e:
        print(f"\nError generating content for '{title}': {str(e)}")
        print("Please select a different article.")
        return None

def main():
    select_and_generate_articles()

if __name__ == "__main__":
    main()
