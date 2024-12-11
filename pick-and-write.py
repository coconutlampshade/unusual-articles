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
    title = url.split('/')[-1].replace('_', ' ')
    return title

def select_article():
    articles = get_random_articles(5)
    print("\nHere are 5 random articles. Please select one (1-5):")
    for idx, url in enumerate(articles, 1):
        title = get_title_from_url(url)
        print(f"{idx}. {title}")
        print(f"   {url}\n")
    
    while True:
        try:
            choice = int(input("Enter your choice (1-5): "))
            if 1 <= choice <= 5:
                return articles[choice - 1]
            else:
                print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")

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
        Write a 300-word blog post about {title}. 
        Use this Wikipedia content as your source: {content[:2000]}...
        
        Content Structure Requirements:
        1. Open with an attention-grabbing first sentence highlighting the most fascinating aspect
        2. Write 2-3 tight paragraphs explaining the core concept/story
        3. Include at least 2 direct quotes from the Wikipedia article
        4. Include the Wikipedia URL as a reference
        5. End with a thought-provoking takeaway or modern relevance
        
        Writing Style Requirements:
        6. Use clear, conversational language - avoid academic/encyclopedic tone
        7. Transform dry facts into engaging narrative
        8. Include specific details rather than generalizations
        9. Limit dates/numbers to only the most essential ones
        10. Break up complex ideas into digestible pieces
        11. Write in the style of Mental Floss and Atlas Obscura
        12. Use humor and wit where appropriate
        13. Don't use subheadings
        
        Content Selection Guidelines:
        14. Focus on the most compelling 20% of the article
        15. Skip obvious background information
        16. Emphasize human elements and storytelling opportunities
        17. Highlight modern relevance or contemporary significance
        18. Include at least one surprising or counterintuitive fact
        19. Handle mature topics with academic professionalism
        
        Specific Don'ts:
        20. Don't try to cover everything
        21. Don't copy Wikipedia's language or structure
        22. Don't get bogged down in technical details
        23. Don't include tangential information
        24. Don't end with a weak summary
        
        Format Requirements:
        25. Format in markdown with proper headings and links
        26. Include an SEO-friendly title
        27. Keep to approximately 300 words
        28. Ensure proper flow between paragraphs
        29. Use appropriate terminology for academic/historical context
        
         IMPORTANT LENGTH REQUIREMENTS:
        - The final post MUST be 350 words (excluding title and URL)
        - Each paragraph should be 80-100 words
        - Do not include subheadings or bullet points
        - Count your words carefully and adjust until you reach exactly 350
        
        Before Generating:
        - Count words in each paragraph to ensure 350 total
        - Verify substantive content fills the word count (no fluff)
        - Ensure proper distribution of content across paragraphs
        - Verify word count is close to 300
        - Ensure opening sentence hooks readers
        - Confirm ending provides value/insight
        - Fact-check any surprising claims
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
    # Get user selection
    article_url = select_article()
    print(f"\nSelected article: {article_url}")
    
    # Fetch content
    title, content, url = fetch_wikipedia_content(article_url)
    print(f"Generating blog post about: {title}")
    
    # Generate blog post
    blog_post = generate_blog_post(title, content, url)
    
    if blog_post:
        # Save to file with title as filename
        filename = f"blog_posts/{title.lower().replace(' ', '_')}.md"
        os.makedirs('blog_posts', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(blog_post)
        
        print(f"Blog post saved to: {filename}")
        print("\nBlog post content:")
        print("=" * 50)
        print(blog_post)
    else:
        print("Failed to generate blog post. Please try another article.")

if __name__ == "__main__":
    main()
