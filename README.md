# WikiWriter

A Python web application that generates engaging blog posts from Wikipedia's unusual articles using Google's Gemini AI.

## Scripts

### unusual.py
- Scrapes the [Wikipedia:Unusual articles](https://en.wikipedia.org/wiki/Wikipedia:Unusual_articles) page
- Creates `unusual_articles.txt` containing URLs of all unusual articles
- Only needs to be run once to create/update your article database

### pick-and-write.py
- Main script for generating blog posts
- Reads from `unusual_articles.txt`
- Shows 5 random articles at a time
- Generates 350-word blog posts using Gemini AI
- Press 'S' to see 5 new random articles
