import argparse
import asyncio
import requests
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, SecretStr
import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
import json  



genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

prompt_template3 = """
You are an assistant that heps people in searching youtube video, getting transcripts or summarisation from youtube videos.
{query} is what the user has provided. From this identify whether
1)action - respond 'transcript', 'summary' or 'search'
2)query - return the words to search if the user wants to search or the url from query


Respond a json which has action and query:
"""


class CustomSecretStr(SecretStr):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, **kwargs):
        field_schema.update(type="string", writeOnly=True, format="password")
        return field_schema

class CustomChatGroq(ChatGroq):
    groq_api_key: CustomSecretStr

llm = CustomChatGroq(
    groq_api_key=CustomSecretStr(os.getenv("GROQ_API_KEY")),
    model_name="llama3-70b-8192"
)


# Define the chat prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that summarizes the given text for the user in a more understandable format for easy interpretation.",
        ),
        ("human", "{input}"),
    ]
)

# Combine the prompt with the language model (llm)
chain = prompt | llm

def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get('v')
    return video_id[0] if video_id else None

def search_youtube(query):
    api_key = os.getenv("YOUTUBE_API_KEY")  # Replace with your YouTube Data API key
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={api_key}&type=video"
    response = requests.get(search_url)
    results = response.json()
    videos = [{
        'id': item['id']['videoId'],
        'title': item['snippet']['title']
    } for item in results.get('items', [])]
    return videos

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([item['text'] for item in transcript])
    except Exception as e:
        return f'Error fetching transcript: {str(e)}'


#can't use asychronous for out use case
# async def summarize_with_groq(text_chunk):
#     try:
#         result = await asyncio.to_thread(
#             lambda: chain.invoke(
#                 {
#                     "input_language": "English",
#                     "output_language": "English",
#                     "input": text_chunk,
#                 }
#             )
#         )
#         return result.content
#     except Exception as e:
#         return f"Error summarizing chunk: {str(e)}"

# async def summarize_text_async(chunks):
#     tasks = [summarize_with_groq(chunk) for chunk in chunks]
#     return await asyncio.gather(*tasks)

# def summarize(video_id):
#     try:
#         transcript = get_transcript(video_id)
#         chunk_size = 3000
#         chunks = [transcript[i:i + chunk_size] for i in range(0, len(transcript), chunk_size)]
#         summaries = asyncio.run(summarize_text_async(chunks))
#         return "\n".join(summaries)
#     except Exception as e:
#         return f'Error summarizing transcript: {str(e)}'

def summarize_with_groq(text_chunk):
    try:
        result = chain.invoke(
            {
                "input_language": "English",
                "output_language": "English",
                "input": text_chunk,
            }
        )
        return result.content
    except Exception as e:
        return f"Error summarizing chunk: {str(e)}"

def summarize(video_id):
    try:
        transcript = get_transcript(video_id)
        chunk_size = 3000
        chunks = [transcript[i:i + chunk_size] for i in range(0, len(transcript), chunk_size)]
        summaries = [summarize_with_groq(chunk) for chunk in chunks]
        return "\n".join(summaries)
    except Exception as e:
        return f'Error summarizing transcript: {str(e)}'


# def youtube_function(query):
#     prompt = prompt_template3.format(query=query)
#     response = model.generate_content(prompt)
    
#     response_text = response.candidates[0].content.parts[0].text
    
#     json_str = response_text.strip("```json\n").strip("``` \n")
    
#     try:
#         action_query = json.loads(json_str)
#         action = action_query.get("action")
#         query = action_query.get("query")
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON: {e}")
#         return

#     if action == "search":
#         videos = search_youtube(query)
#         l=[]
#         for video in videos:
#             l.append(f"Video : {video}\nVideo URL: https://www.youtube.com/watch?v={video['id']}Title: {video['title']}")
#             # print(video)
#             # print(f"Video URL: https://www.youtube.com/watch?v={video['id']}")
#             # print(f"Title: {video['title']}")
#             # print("---")
#         return "".join(l)
#     elif action == "transcript":
#         video_id = get_video_id(query)
#         if video_id:
#             transcript = get_transcript(video_id)
#             return(transcript)
#         else:
#             return("Invalid YouTube URL")
#     elif action == "summary":
#         video_id = get_video_id(query)
#         if video_id:
#             summary = summarize(video_id)
#             return(summary)
#         else:
#             return("Invalid YouTube URL")

import json
from typing import Dict, Any

def youtube_function(query: str) -> Dict[str, Any]:
    prompt = prompt_template3.format(query=query)
    response = model.generate_content(prompt)
    
    response_text = response.candidates[0].content.parts[0].text
    
    json_str = response_text.strip("```json\n").strip("``` \n")
    
    try:
        action_query = json.loads(json_str)
        action = action_query.get("action")
        query = action_query.get("query")
    except json.JSONDecodeError as e:
        return {
            "name": "final_answer",
            "parameters": {
                "text": f"Error decoding JSON: {e}. Please try rephrasing your request."
            }
        }

    if action == "search":
        videos = search_youtube(query)
        results = []
        for video in videos:
            results.append(f"Video ID: {video['id']}\nTitle: {video['title']}\nURL: https://www.youtube.com/watch?v={video['id']}")
        return {
            "name": "youtube_search",
            "parameters": {
                "query": query,
                "results": "\n\n".join(results)
            }
        }
    elif action == "transcript":
        video_id = get_video_id(query)
        if video_id:
            transcript = get_transcript(video_id)
            return {
                "name": "youtube_transcript",
                "parameters": {
                    "video_id": video_id,
                    "transcript": transcript
                }
            }
        else:
            return {
                "name": "final_answer",
                "parameters": {
                    "text": "Invalid YouTube URL. Please provide a valid YouTube video URL."
                }
            }
    elif action == "summary":
        video_id = get_video_id(query)
        if video_id:
            summary = summarize(video_id)
            return {
                "name": "youtube_summary",
                "parameters": {
                    "video_id": video_id,
                    "summary": summary
                }
            }
        else:
            return {
                "name": "final_answer",
                "parameters": {
                    "text": "Invalid YouTube URL. Please provide a valid YouTube video URL."
                }
            }
    else:
        return {
            "name": "final_answer",
            "parameters": {
                "text": f"Unknown action: {action}. Please try rephrasing your request."
            }
        }


