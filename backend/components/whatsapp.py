import pywhatkit
import requests
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

#to get name and content
prompt_template3 = """
You are an assistant that heps people in sending whatsapp messages.
{query} is what the user has provided. From this identify the message that the user wants to send and the message content.
Once done, you will have the folllowing
1)Name - to whom the user wants to send
2)Message - the content of the message(Modify this content to phrase it properly)

Respond only name and message_content:
Respond only in the format : 
Name: name
Message: message
"""

contacts={'amma':'9962976755','appa':'9381086647','aswath':'7010348134','Aswath':'7010348134'}
#will be integrated with google calender to fetch all contacts and also with twilio API
#for testing use some numbers

def send_whatsapp_message(phone_number, message):
    # Remove any non-digit characters from the phone number
    phone_number = ''.join(filter(str.isdigit, phone_number))
    
    # Add country code if not present (assuming US, modify as needed)
    if len(phone_number) == 10:
        phone_number = f"+91{phone_number}"
    elif not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"
    
    # Send WhatsApp message
    try:
        pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=10)
        return "WhatsApp message sent successfully"
    except Exception as e:
        return f"Failed to send WhatsApp message: {str(e)}"

def whatsapp_message(query):
    prompt = prompt_template3.format(query=query)
    response = model.generate_content(prompt)    
    # print(response.text)
    lines = response.text.split('\n')
    print("\n1",lines,"1\n")
    name = lines[0].split(' ')[1].strip()  
    message = lines[1].split(' ')[1].strip()
    # name = response.text.split()[0]
    # message=response.text.split(name)[1]
    phone_number=contacts[name]
    # print(phone_number,'\n',message)
    # message = input("Enter your message: ")
    result = send_whatsapp_message(phone_number, message)
    return result


