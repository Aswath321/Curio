
# Meet Curio: Your Multi-Purpose Conversational AI Assistant

## Welcome to the Future of Personalized Assistance!

Imagine a smart assistant that understands your voice commands, manages administrative tasks effortlessly, and even processes files like a pro. That's **Curio** – your next-gen AI-powered assistant designed to elevate productivity and streamline workflows.

Curio isn't just another chatbot. It’s a multi-purpose assistant that handles everything from file uploads and parsing to voice-based interactions. Whether it’s student project tracking, posting updates on LinkedIn, or generating flashcards from PDFs, Curio’s got your back!



### Key Features

1. **Multi-Modal Communication**
   - Text-based conversations
   - Voice recognition for hands-free interaction
   - Human-like voice responses for a more immersive experience with deepgram

2. **AI Agent**
   - Takes autonomous decision for tool handling facilitating langchain for workflow
      
3.**Smart and Adaptive AI**
   - Contextual understanding of conversations for smoother interactions due to knowledge graph construction

3. **Task Automation**
   - **Email Management**: Send and retrieve emails with easy-to-use commands. Send mails to multiple accounts at the same time
   - **Calendar Integration**: Manage your schedule - add, view, and modify events.
   - **Reminders**: Set and prioritize reminders - low, medium and high that will get added to your google calender
   - **Generate Flashcards**: Upload PDF documents and even generate flashcards.
   - **GitHub Repository Management**: Create, update, and manage repos directly from Curio.

4. **File Handling & Parsing**
   - Ability to upload multiple files for analysis. Curio parses key data, stores them in **AWS S3** and access them using **AWS Cloudfront** for scalability, and generates summaries or insights from documents.
   - Supported formats: PDFs, CSVs and Documents.

5. **Fun and Engaging Features**
   - Play a fun **mystery game** to take a break.
   - Generate **flashcards** from documents for studying.

6. **Seamless Web Scraping**
   - Scrape product details from Amazon and other websites (more coming soon).

7. **Personalized Recipe Finder**
   - Get recipe recommendations based on your preferences.

8. **Web Search** - For real time results

9. **Group Chat** - For interacting with peers and also with AI

10. **Trumio-Specific Automations**:
   - **Student Project Tracking**: Keep tabs on ongoing projects with status updates, deadlines, and progress reportsp.
   - **LinkedIn Post Automation**: Post client updates using predefined templates with Trumio’s credentials via the LinkedIn API.
   - **Project Suggestions for Students**: Leverage AI to analyze student-provided information or resumes and suggest suitable projects.

11.**Local LLM** - Access private and safe conversation with an offline assistant where your data does not leaked.



### How to Set Up Curio

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/curio-ai-assistant.git
   ```

2. **Backend Setup**:
   - Install dependencies and set up the database:
     ```bash
     cd backend
     pip install -r requirements.txt
     python setup_db.py
     uvicorn main:app --reload
     ```
   - Create a `.env` file with API keys for Google, AWS, and Hugging Face.

3. **Frontend Setup**:
   ```bash
   cd src
   npm install
   npm start
   ```

4. **Access Curio**: Open `http://localhost:3000` to start using Curio.

5. Run backends for group_chat seperately


---

With **Curio**, you’re not just getting a chatbot; you're getting a fully personalized assistant that grows with you. Ready to transform the way you interact with your digital world?

