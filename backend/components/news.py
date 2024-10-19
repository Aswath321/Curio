import requests
from dotenv import load_dotenv
load_dotenv()
import os

gemini_api_key = os.getenv("GOOGLE_API_KEY")
gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"  # Corrected URL

# Predefined categories
CATEGORIES = [
    "business", "entertainment", "general", 
    "health", "science", "sports", "technology"
]

# Function to fetch latest news
def get_latest_news():
    try:
        api_key = os.getenv("NEWS_API_KEY")
        url = f"https://newsapi.org/v2/everything?q=latest news&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get('articles', [])
    except Exception as e:
        print(f"Error fetching latest news: {e}")
        return "Error retrieving news at the moment."

# Function to fetch news based on a search query
def get_news_by_keyword(query):
    try:
        api_key = os.getenv("NEWS_API_KEY")
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get('articles', [])
    except Exception as e:
        print(f"Error fetching news by keyword: {e}")
        return "Error retrieving news at the moment."

# Function to fetch top headlines based on category
def get_top_headlines(category):
    try:
        api_key = os.getenv("NEWS_API_KEY")
        url = f"https://newsapi.org/v2/top-headlines?category={category}&apiKey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get('articles', [])
    except Exception as e:
        print(f"Error fetching top headlines: {e}")
        return "Error retrieving news at the moment."

# Function to summarize the news and filter out unwanted entries
def summarize_news(articles):
    summaries = []
    for article in articles:
        title = article.get('title')
        description = article.get('description', "No description available.")
        url = article.get('url')

        # Filtering condition to exclude unwanted articles
        if title and url and "Removed" not in title and "Removed" not in description and "removed" not in url:
            summary = f"Title: {title}\nDescription: {description}\nRead more: {url}\n"
            summaries.append(summary)

    return summaries

# Function to classify user prompt using Gemini's API
def classify_prompt(prompt):
    try:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"Classify the following prompt into 'latest news', 'category', or 'keyword': '{prompt}'"
                        }
                    ]
                }
            ]
        }

        # Make the API call to Gemini
        response = requests.post(gemini_api_url, headers=headers, json=data, params={'key': gemini_api_key})
        response.raise_for_status()

        # Extract the content of the response
        classification = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return classification.strip().lower()
    except Exception as e:
        print(f"Error classifying prompt: {e}")
        return None

# Main function to handle user input and return summarized news
def get_news(prompt):
    prompt = prompt.lower().strip()

    # Classify the user prompt using Gemini
    classification = classify_prompt(prompt)

    if classification:
        if "latest news" in classification:
            articles = get_latest_news()
        elif any(category in classification for category in CATEGORIES):
            category = next(category for category in CATEGORIES if category in classification)
            articles = get_top_headlines(category)
        else:
            articles = get_news_by_keyword(prompt)
    else:
        return "Unable to classify the prompt."

    # Summarize and display the news
    if articles and isinstance(articles, list):
        summaries = summarize_news(articles)
        l = []
        if summaries:
            l.append("\nHere are the top news summaries:\n\n")
            for i, summary in enumerate(summaries[:5], 1):  # Show top 5 news summaries
                l.append(f"News {i}:\n{summary}\n\n")
            return "".join(l)
        else:
            return "No valid news articles found after filtering."
    else:
        return "Error retrieving news at the moment."
