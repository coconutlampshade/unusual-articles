import requests
from bs4 import BeautifulSoup

# Fetch and process the Wikipedia page
url = "https://en.wikipedia.org/wiki/Wikipedia:Unusual_articles"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the main content div
content_div = soup.find('div', {'id': 'mw-content-text'})

# Find all links in the main content
urls = []
if content_div:
    for link in content_div.find_all('a'):
        href = link.get('href')
        # Only get Wikipedia article links (internal links that start with /wiki/)
        if href and href.startswith('/wiki/') and ':' not in href:
            full_url = 'https://en.wikipedia.org' + href
            if full_url not in urls:  # Avoid duplicates
                urls.append(full_url)

# Write URLs to a file
with open('unusual_articles.txt', 'w', encoding='utf-8') as f:
    for idx, url in enumerate(urls, 1):
        f.write(f"{idx}. {url}\n")

print(f"Written {len(urls)} URLs to unusual_articles.txt")
