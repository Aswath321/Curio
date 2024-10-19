import os
import base64
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) 
model1 = genai.GenerativeModel('gemini-1.5-flash')

#Extract Url of image and user query
#In the next iteration, option ton uploaf images will be added to ask questions from

prompt_template5 = """
You are an assistant that helps in identifying the url and query for an image from the input.
{query} is the input given by the user.
Your job is to identify the url (example: '/Users/aswath/Desktop/2.jpg') and query(what context the user has asked), and return them in two lines.

Response:
URL
QUERY

Sample Query: /Users/aswath/Desktop/1.png give me a dexcription of the image
Sample Response:
/Users/aswath/Desktop/1.png
give me a dexcription of the image
"""


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/aswath/Desktop/ethos/components/image.json"
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/image_credentials.json" #check readme.md on how to obtain


model2 = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def image_qa(image_path, question):
    try:
        # Load the image and encode it as base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Create a message with the image and question
        message = HumanMessage(
            content=[
                {"type": "text", "text": question},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        )

        # Get the response from Gemini
        response = model2.invoke([message])

        return response.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_description(query):
    prompt = prompt_template5.format(query=query)
    response = model1.generate_content(prompt)

    try:
        lines = response.text.strip().split('\n')
        image_path = lines[0]
        print('\nimage path:',image_path,"1\n")
        question = lines[1]
        answer = image_qa(image_path, question)
        if answer:
            return(answer)
        else:
            return("Failed to get an answer.")
    except (IndexError, ValueError):
        return(f"Failed to parse response: {response.text}")


   