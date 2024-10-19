import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import google.generativeai as genai
from dotenv import load_dotenv
import os


#to load env variables
load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')


#Review Summarisation
prompt_template1 = """
You are an AI assistant. The following is a product description scraped from Amazon : {query}.
Your task is to analyze this description and create a concise summary that highlights the most important and relevant features of the product for potential users.
Focus on the key selling points, unique features, and any benefits the user would find valuable.
Make the response short, crisp, and user-friendly.


Response:
"""


#Retrieve product name
prompt_template2 = """
You are an assistant.
{query} is the user's query to search a product on amazon. It's your duty to figure out what the product is and retrieve it.
You should return only the name of the product 

Response (Product name alone):
"""



user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
]


def get_random_user_agent():
    return random.choice(user_agents)


def make_request(url, max_retries=5, delay=1):
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.amazon.in',
        'Connection': 'keep-alive'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  
                print(f"Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Unable to fetch the data.")
                return None


def format_amazon_results(products):
    formatted_results = "# Amazon Search Results\n\n"
    for i, product in enumerate(products, 1):
        formatted_results += f"## Product {i}\n"
        formatted_results += f"- **Title**: {product['Title']}\n"
        formatted_results += f"- **Price**: {product['Price']}\n"
        formatted_results += f"- **Rating**: {product['Rating']}\n"
        formatted_results += f"- **URL**: {product['URL']}\n\n"
    return formatted_results


def scrape_amazon(query):
    try:
        # Generate content for the product
        prompt = prompt_template2.format(query=query)
        response = model.generate_content(prompt)
        product = response.text

        # Construct the Amazon search URL
        url = f"https://www.amazon.in/s?k={quote_plus(product)}"
        
        # Make a request to the Amazon page
        response = make_request(url)
        if not response:
            return "Failed to retrieve data from Amazon after multiple attempts."
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Select the first search result
        results = soup.select('.s-result-item[data-component-type="s-search-result"]')[:1]
        if not results:
            return "No results found"
        
        products = []
        
        # Loop through results to extract product data
        for result in results:
            title = result.select_one('.a-text-normal')
            price = result.select_one('.a-price .a-offscreen')
            product_url = result.select_one('a.a-link-normal')['href']
            
            # Skip if required data is missing
            if not (title and price and product_url):
                continue
            
            # Build the full product URL
            product_url = urljoin('https://www.amazon.in', product_url)
            product_response = make_request(product_url)
            if not product_response:
                continue
            
            product_soup = BeautifulSoup(product_response.text, 'html.parser')
            
            # Extract additional product details
            offers = product_soup.select_one('span.aok-offscreen')
            offers_text = offers.get_text(strip=True) if offers else "No offers found"
            
            rating = product_soup.select('span.a-size-base.a-color-base')
            rating_text = rating[1].get_text(strip=True) if len(rating) >= 2 else ""
            
            delivery = product_soup.select_one('#deliveryBlockMessage')
            delivery_text = delivery.get_text(strip=True) if delivery else "Delivery information not available"
            
            about_item = product_soup.select('li span.a-list-item')
            description_text = " ".join([i.get_text(strip=True) for i in about_item]) if about_item else "No description available"
            
            # Generate content based on the product description
            prompt = prompt_template1.format(query=description_text)
            response = model.generate_content(prompt)
            description_text = response.text
            
            customer_reviews_grouped = product_soup.select_one('p.a-spacing-small span')
            customer_reviews = customer_reviews_grouped.get_text(strip=True) if customer_reviews_grouped else "Not available"
            
            # Append the product details to the products list
            products.append({
                'title': title.text.strip(),
                'price': price.text.strip(),
                'offers': offers_text,
                'rating': rating_text,
                'delivery': delivery_text,
                'url': product_url,
                'description': description_text,
                'customer_reviews': customer_reviews,
            })
        
        # If no products were successfully extracted
        if not products:
            return "Failed to extract product information"
        
        # Format and return the product information
        result = ""
        for idx, product in enumerate(products, 1):
            result += f"""\nProduct:
            **Title:** {product['title']}
            **Price:** {product['price']}
            **Offers:** {product['offers']}
            **Delivery:** {product['delivery']}
            **Rating:** {product['rating']}
            **Description:** {product['description']}
            **Customer Reviews(Summarized):** {product['customer_reviews']}\n
            **URL:** {product['url']}\n\n\n\n"""
        
        return result
    
    except Exception as e:
        # Return a message if an error occurs or no product is found
        return f"An error occurred: {str(e)} or no product found."
