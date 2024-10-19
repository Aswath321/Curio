import os
import asyncio
from crawl4ai import AsyncWebCrawler
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq
groq_api_key = os.environ['GROQ_API_KEY']
llm_groq = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-70b-8192",
    temperature=0.2
)

async def ask_groq(query, context):
    """Use Groq to process query and context"""
    prompt = f"""You are a technical documentation expert. Your task is to extract specific technical implementation details from the provided context based on the query.

    Guidelines:
    - Focus only on code examples and implementation details
    - If the query asks about specific implementation steps, provide those exact steps from the context
    - Include any relevant code snippets exactly as they appear in the context
    - Do not add explanations or interpretations unless specifically asked
    - If the information is not in the context, say "Information not found in the provided content"

    Query: {query}
    Context: {context}

    Response format:
    1. Direct answer to the query using only information from the context
    2. Any relevant code snippets (if present in the context)
    """

    try:
        response = await asyncio.to_thread(llm_groq.invoke, prompt)
        return response.content
    except Exception as e:
        return f"Error processing with Groq: {str(e)}"

async def extract_website_and_query(user_input):
    """Use Groq to extract website and query"""
    prompt = f"""
    You are a technical query parser. Analyze the following user input and extract the website URL and the specific technical query.

    Input: {user_input}

    Rules for extraction:
    1. The website URL should be a complete URL starting with http:// or https://
    2. The query should focus on technical implementation details, coding patterns, or specific features
    3. If multiple questions are present, focus on the most specific technical question

    Output format (exactly as shown):
    Website: <extracted URL>
    Query: <specific technical question>

    Do not add any other text or explanations.
    """

    try:
        response = await asyncio.to_thread(llm_groq.invoke, prompt)
        extracted_info = response.content

        lines = extracted_info.split("\n")
        website = lines[0].split("Website:")[1].strip()
        query = lines[1].split("Query:")[1].strip()
        return website, query
    except Exception as e:
        raise ValueError(f"Could not extract website and query from the input: {str(e)}")

async def main(website):
    """Scrape website content"""
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=website)
        with open("scraped_data.txt", "w", encoding='utf-8') as file:
            file.write(str(result.markdown))

def load_scraped_data(filename="scraped_data.txt"):
    """Load scraped content from file"""
    with open(filename, "r", encoding='utf-8') as file:
        data = file.read()
    return data

async def web_scrape(query):
    """Main function to handle web scraping and query processing"""
    try:
        # Extract website and query
        website, extracted_query = await extract_website_and_query(query)
        print(f"Extracted Website: {website}")
        print(f"Extracted Query: {extracted_query}")
        
        # Scrape website
        await main(website)
        scraped_data = load_scraped_data()
        
        # Process query
        if "prompt" in extracted_query.lower() and "system message" in extracted_query.lower():
            enhanced_query = "Explain how to create a prompt with system message and create a chain, including any specific code examples or implementation steps."
        else:
            enhanced_query = extracted_query
            
        # Get answer from Groq
        answer = await ask_groq(enhanced_query, scraped_data)
        
        # Save response
        with open('/Users/aswath/Desktop/ethos/ethos/backend/components/agent_res.txt', 'w', encoding='utf-8') as f:
            f.write(answer)
            
        return answer

    except Exception as e:
        error_message = f"Error during web scraping: {str(e)}"
        print(error_message)
        return error_message



# if __name__ == "__main__":
#     query = "web scrape https://medium.com/google-developer-experts/beyond-live-sessions-building-persistent-memory-chatbots-with-langchain-gemini-pro-and-firebase-19d6f84e21d3 and tell me how to add a prompt with system message and create a chain?"
#     query="web scrape https://readmedium.com/en/https:/byrayray.medium.com/llama-3-2-vs-llama-3-1-vs-gemma-2-finding-the-best-open-source-llm-for-content-creation-1f6085c9f87a and tell me why llama 2 stands out for content creation"
#     asyncio.run(web_scrape(query))

with open('/Users/aswath/Desktop/ethos/ethos/backend/components/web_scrape_content.txt') as f:
    query=f.read()
asyncio.run(web_scrape(query))