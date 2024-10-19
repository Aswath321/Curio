# Meet Curio: More than just a conversational AI - Assistant

## Welcome to the Future of Personal Assistance!

Imagine having a super-smart friend who's always ready to help you out, learns what you like, and fits right into your digital world. That's Curio – your new AI assistant that helps in day to day tasks.

Curio isn't your average chatbot. It's a game-changer in how we interact with AI, mixing smart tech with real-world usefulness. Need to sort out your emails? Plan your meals? Get the latest news? etc. Curio's got your back. Think of it as your go-to tool for, well, pretty much everything!

The coolest part? Curio gets smarter with every chat. It learns your style, your preferences, and becomes more like you over time. It's not just an assistant; it's like having a mini-you in your pocket. It has an autonomous agent that decides what task to do based on the query.

Check out what Curio can do!

###  What Curio Brings to the Table

1. **Talk to Curio Your Way**
   - Chat with text
   - Use your voice when your hands are full
   - Let Curio talk back to you

2. **AI That Works for You**
   - Curio picks the right tool for each task
   - Gets better at helping you over time by constantly evolving based on user queries

3. **Your Personal Task Wizard**

   - Infobox - Get a quick glance on important tasks for the day
   ![Example_Image](images/infobox.png)

    - Answers your questions smartly
    ![Example Image](images/basic.png)

   - Web Scraping - Amazon (Will add more sites to scrape from)
    ![Example Image](images/scrape.png)

   - Sends WhatsApp messages for you
    ![Example Image](images/whatsapp.png)

   - Manages your emails - Send mails without giving mail ID's, retreive mails based on query
    ![Example Image](images/gmail.png)
    ![Example Image](images/gmail2.png)

   - Keeps your calendar in check by adding and viewing events
    ![Example Image](images/calender.png)

   - Sets reminders (and knows what's urgent) based on priority level
    ![Example Image](images/reminder.png)

   - Tells you what's in pictures
    ![Example Image](images/image.png)

   - Finds recipes you'll love
    ![Example Image](images/recipe.png)

   - Helps you understand PDF documents  (Create a PDF RAG from multiple documents to ask questions from)

   - Automated Linkedin posting

   - Manages your YouTube stuff - Search for YT videos, trnascript and summarise youtube videos
    ![Example Image](images/yt.png)
    ![Example Image](images/yt2.png)

   - Handles your GitHub like a pro - create repo, add files to repo, searh for something in global repo's etc
    ![Example Image](images/github.png)

   - Brings personalised news
    ![Example Image](images/news.png)

   - Searches the web and summarises for you - ensures authenticity and up to date news
    ![Example Image](images/websearch.png)

5. **Chats That Make Sense**
   - Understands the context of your conversation
   - Remembers your preferences
   - Keeps track of your chat to give better answers (Persistent Memory)
   - Multilingual Support( Has tamil atm)

6. **Easy-to-Use Design**
   - Smooth, React-based interface
   - See your chat history in real-time

### Tech Stack

- **Frontend**: React.js 
- **Backend**: FastAPI (speedy and reliable)
- **Database**: SQLite (light, embedded and flawlesss)
- **AI**: 
  - Google's Gemini and Meta's Llama
  - LangChain for smart conversations
- **API's**: Gmail, Calendar, News, and more
- **Additional**: Axios for web stuff, Hugging Face for translations

### Next iteration of Curio includes :

1. Real-time chat: Ask multiple questions without waiting for the response of the previous ones!
2. Combining multiple LLM's: To get the best response
3. Testing with local LLM: Ensuring security
4. Making Curio self-improving: Help it learn on its own to make personalised recommendations by using reinforcement learning and understanding user needs
5. Video RAG: Chat about videos 
6. Websockets
7. Give podcasts and it will extract the parts personalised to you saving loads of time
8. More sites to scrape from
9. Connecting with more API's with flawless integration
10. Seamlessly plan your trips


### Get Curio Up and Running

1. Clone the repo:
   ```
   git clone https://github.com/your-username/curio-ai-assistant.git

   ```

2. Run backend/setup_db.py to setup the database

3. Set up the backend:
   Create a Google Cloud Account
   In the python files, wherever path/to/credentials.json is there, replace it with json credentials from GCP.
   Go to https://console.cloud.google.com/apis/credentials?project=ethos-436204 and create o-auth 2.0 Client-ID and download the json file. 
   Enable necessart API's in Google Cloud

   ```
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

4. Add your secret keys:
   Get respective API's and add it to .env file. .sample_env is attached for reference. Replace API keys and rename to .env
   - Make a `.env` file in the backend folder
   - Put in your API keys (Google, Hugging Face, etc.)
  

5.  Set up the frontend:
   ```
   cd src
   npm install
   npm start
   ```

6. View - `http://localhost:3001`

### Future Enhacements !

In the future, we're dreaming of:
- Connecting Curio to your smart home gadgets
- Making conversations even more natural
- Predicting what you need before you ask
- Linking up with all your favorite local apps
- Giving Curio a voice that matches your mood
- Full voice conversations where you can chat back and forth, just like with a friend and also interrupt in between and ask the next question

---
