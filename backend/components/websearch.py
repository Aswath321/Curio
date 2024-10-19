import dotenv
import argparse
import locale
import os
import sys
import re
import requests
import time
import tempfile
from langchain_groq import ChatGroq
import trafilatura
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import pysbd
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional

# Load environment variables
import dotenv

dotenv.load_dotenv()

# Replace with your Google Custom Search Engine ID and API Key
API_KEY = os.getenv("CSE_API_KEY")  # Replace with your actual API key
CSE_ID = os.getenv("CSE_ID")   # Replace with your actual CSE ID

# Initialize Groq client
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),  # Use environment variable
    model_name="llama3-70b-8192"
)

# Define the chat prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that summarizes the given text."),
    ("human", "{input}"),
])
chain = prompt | llm
seg = pysbd.Segmenter(language='en')
SUMMARY_TASK = "Summary Instructions:\n- List key points:\n- Use bullet points."

language_data = {
    'en': {'region': 'US'},
    'hi': {'region': 'IN'},
}

def request_headers(language_code='en'):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'Accept-Language': f"{language_code}-{language_data.get(language_code, {}).get('region', 'US')},{language_code};q=0.8"
    }
    return headers

def extract_youtube_video_id(url: str) -> Optional[str]:
    found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
    return found.group(1) if found else None

def get_video_transcript(video_id: str, language: str) -> Optional[str]:
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return ' '.join([line["text"] for line in transcript])
    except (NoTranscriptFound, TranscriptsDisabled):
        return None

def fetch_url_content(url: str, language: str) -> str:
    start_time = time.time()  # Start timing
    video_id = extract_youtube_video_id(url)
    if video_id:
        result = get_video_transcript(video_id, language)
    else:
        response = requests.get(url, headers=request_headers(language))
        if response.status_code == 200 and 'text/' in response.headers['content-type']:
            result = trafilatura.extract(response.text, output_format='txt', target_language=language)
        else:
            filename = response.headers.get('Content-Disposition', os.path.basename(url)).split('filename=')[-1].strip('"')
            with tempfile.NamedTemporaryFile(delete=True, suffix=filename) as tmp_file:
                tmp_file.write(response.content)
                result = get_file_text(tmp_file.name, language)

    latency = time.time() - start_time  # Calculate latency
    print(f"Fetching content latency: {latency:.2f} seconds")
    return result

def get_file_text(filename: str, language: str) -> str:
    with open(filename, 'r') as f:
        return f.read()

def summarize_with_groq(text_chunk: str, max_retries: int = 5) -> str:
    input_data = {
        "input_language": "English",
        "output_language": "English",
        "input": SUMMARY_TASK + "\n" + text_chunk,
    }
    retries = 0
    while retries < max_retries:
        try:
            result = chain.invoke(input_data)
            return result.content
        except Exception as e:
            error_message = str(e)
            if "rate_limit_exceeded" in error_message:
                # Extract wait time from the error message using regex
                wait_time_match = re.search(r'Please try again in (\d+(\.\d+)?)s', error_message)
                wait_time = float(wait_time_match.group(1)) if wait_time_match else 5  # Default wait time is 5 seconds
                print(f"Rate limit reached. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)  # Wait before retrying
                retries += 1
            else:
                print(f"Error summarizing chunk: {error_message}")
                break
    return f"Failed to summarize after {max_retries} retries."

def chunk_large_text(text_list: list, max_size: int) -> list[str]:
    txts = []
    para = ''
    for s in text_list:
        s_len = len(s)
        if para and len(para) + s_len > max_size:
            txts.append(para)
            para = ''
        if s_len <= max_size:
            para += s + '\n'
        else:
            if para:
                txts.append(para)
                para = ''
            cut = s_len // max_size
            chunk = s_len // (cut + 1)
            i = 0
            while i < s_len:
                if s_len - i <= chunk:
                    txts.append('… ' + s[i:] + ' …')
                    break
                clip_i = s.find(' ', i + chunk)
                txts.append('… ' + s[i:clip_i] + ' …')
                i = clip_i + 1
    if para:
        txts.append(para)
    return txts

def summarize_large_text(text: str, max_size: int, progress=False) -> str:
    text_list = seg.segment(text)
    txts = chunk_large_text(text_list, max_size)
    summaries = [summarize_with_groq(t) for t in txts]
    return '\n'.join(summaries)

def is_allowed_domain(url: str) -> bool:
    """
    Checks if the URL is from an allowed domain (non-social media).
    """
    excluded_domains = ['twitter.com', 'instagram.com', 'facebook.com', 'tiktok.com', 'linkedin.com', 'pinterest.com']
    domain = re.findall(r'://(?:www\.)?([^/]+)', url)
    return not any(excluded in domain[0] for excluded in excluded_domains) if domain else False

def get_top_articles(query, num_results=5):
    """
    Fetches the URLs of top articles based on the search term.
    
    Args:
        query (str): The search term.
        num_results (int): Number of results to fetch (max 5).
    
    Returns:
        list: A list of URLs of the top articles.
    """
    try:
        # Base URL for the Custom Search API
        url = 'https://customsearch.googleapis.com/customsearch/v1'
        
        # Query parameters
        params = {
            'key': API_KEY,
            'cx': CSE_ID,
            'q': query,
            'num': num_results
        }
        
        # Make the GET request to the API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check for request errors
        
        # Parse the JSON response
        search_results = response.json()
        
        # Extract URLs from the search results
        article_urls = [item['link'] for item in search_results.get('items', [])]
        
        # Filter out URLs from social media platforms
        article_urls = [url for url in article_urls if is_allowed_domain(url)]
        
        if not article_urls:
            print("No articles found for the search term.")
        return article_urls
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching articles: {e}")
        return []

def websearch(query):
    # User input for search term
    search_term = query
    
    # Fetch top article URLs
    top_articles = get_top_articles(search_term, num_results=2)
    l = []
    # print("\nTop Article URLs:")
    l.append("\nTop Article URLs:\n\n")
    for url in top_articles:
        # print(url)
        l.append(url + "\n")
    
    # Initialize an empty string for concatenated content
    combined_content = ""
    
    # Fetch content from each URL and concatenate
    for url in top_articles:
        content = fetch_url_content(url, 'en')
        if content:
            combined_content += content + "\n"
    
    # Summarize the combined content
    if combined_content:
        start_summary = time.time()  # Start timing the summarization
        summary = summarize_large_text(combined_content, 8192, progress=True)
        summary_latency = time.time() - start_summary  # Calculate summarization latency
        print(f"\nSummarization latency: {summary_latency:.2f} seconds")
        
        # Output the final summary
        print("\nFinal Summary of All Fetched Content:")
        return "".join(l) + summary
    else:
        return "No content to summarize."


