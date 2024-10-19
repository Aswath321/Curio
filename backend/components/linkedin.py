from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
from functools import wraps
import os
import requests
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
import re
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    UPLOAD_FOLDER = os.path.join('static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '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')

app.config.from_object(Config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

class LinkedinAutomate:
    def __init__(self, access_token):
        self.access_token = access_token
        self.user_info = None
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self.python_group_list = [9247360]  # Example group ID
        
        # Initialize LangChain components
        self.llm = ChatGroq(
            groq_api_key=Config.GROQ_API_KEY,
            model_name="llama3-70b-8192"
        )
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant helping to create professional LinkedIn posts. Your task is to guide the user through the post creation process by asking relevant questions and collecting necessary information. Keep the conversation focused on creating the LinkedIn post. If the user deviates, gently remind them of the task at hand and guide them back to post creation. Always maintain a professional and helpful tone."),
            ("human", "{human_input}")
        ])
        self.memory = ConversationBufferMemory(return_messages=True)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template, memory=self.memory)
        
        # Image generation setup
        self.image_gen_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        self.image_gen_headers = {
            "Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"
        }
        
        self.post_info = {}
        self.image_folder = app.config['UPLOAD_FOLDER']

    def get_user_info(self):
        """Fetch user information from LinkedIn API"""
        url = "https://api.linkedin.com/v2/userinfo"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            self.user_info = response.json()
            logger.info("Successfully retrieved user info")
            return self.user_info
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching user info: {str(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
            return None

    def generate_question(self):
        """Generate the next question based on the current conversation"""
        prompt = f"""Based on the following information and previous questions, generate the next relevant question to ask the user about their LinkedIn post:

        Current post information:
        {json.dumps(self.post_info, indent=2)}

        Generate a single, specific question that will help gather more information for creating an engaging LinkedIn post.
        """
        
        try:
            response = self.chain.predict(human_input=prompt)
            logger.info("Successfully generated next question")
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            return None

    def generate_post_content(self):
        """Generate LinkedIn post content using LangChain"""
        prompt = f"Based on the following information, generate a professional LinkedIn post:\n\n"
        for key, value in self.post_info.items():
            prompt += f"{key}: {value}\n"
        prompt += "\nWrite in first person as if I'm posting directly. Make it engaging and professional. Start with 'Hello Connections' if it's not already included. Don't include any introductory or concluding phrases. The post should be ready to share as-is. End it with relevant tags."
        
        try:
            response = self.chain.predict(human_input=prompt)
            content = response.strip()
            if not content.startswith("Hello Connections"):
                content = "Hello Connections,\n\n" + content
            logger.info("Successfully generated post content")
            return content
        except Exception as e:
            logger.error(f"Error generating post content: {str(e)}")
            return None

    def generate_image_prompt(self, post_content):
        """Generate a prompt for image generation based on post content"""
        try:
            prompt_request = f"""
            Analyze the following LinkedIn post and generate a vivid, professional image description that captures its essence:

            {post_content}

            Consider the following aspects:
            1. If it's a job posting:
            - Represent the industry or field (e.g., tech, finance, healthcare)
            - Illustrate key skills or tools mentioned
            - Convey company culture or work environment
            2. If it's a job application or career-related post:
            - Depict professional growth or career progression
            - Visualize key skills or achievements mentioned
            - Represent the individual's aspirations or goals
            3. For general professional posts:
            - Capture the main theme or topic
            - Represent any metaphors or analogies used
            - Illustrate key concepts or ideas mentioned

            The image should be:
            - Professional and appropriate for LinkedIn
            - Visually appealing and engaging
            - Relevant to the post's content and tone

            Provide a concise, vivid description suitable for AI image generation, focusing on visual elements, colors, and composition.
            """
            response = self.chain.predict(human_input=prompt_request)
            logger.info("Successfully generated image prompt")
            return response.strip()
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            return None

    def generate_image(self, prompt):
        """Generate an image using HuggingFace's API"""
        try:
            payload = {"inputs": prompt}
            response = requests.post(
                self.image_gen_url,
                headers=self.image_gen_headers,
                json=payload
            )
            response.raise_for_status()
            
            # Save the generated image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = os.path.join(self.image_folder, f'generated_image_{timestamp}.png')
            
            with open(image_path, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Successfully generated and saved image to {image_path}")
            return image_path
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None

    def upload_image(self, image_path):
        """Upload an image to LinkedIn"""
        try:
            # Register upload with LinkedIn
            register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{self.user_info['sub']}",
                    "serviceRelationships": [{
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }]
                }
            }
            
            response = requests.post(register_url, headers=self.headers, json=register_data)
            response.raise_for_status()
            upload_info = response.json()

            # Get upload URL and asset ID
            asset = upload_info['value']['asset']
            upload_url = upload_info['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']

            # Upload the image
            with open(image_path, 'rb') as image_file:
                upload_response = requests.put(
                    upload_url,
                    data=image_file,
                    headers={
                        'Authorization': f'Bearer {self.access_token}'
                    }
                )
                upload_response.raise_for_status()

            logger.info("Successfully uploaded image to LinkedIn")
            return asset
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return None

    def create_post_payload(self, content_type, text, media_asset=None, title=None, feed_type="feed", group_id=None):
        """Create the payload for LinkedIn post"""
        if not self.user_info or 'sub' not in self.user_info:
            raise ValueError("User info not available")

        payload = {
            "author": f"urn:li:person:{self.user_info['sub']}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC" if feed_type == "feed" else "CONTAINER"
            }
        }

        if content_type == "image" and media_asset:
            payload["specificContent"]["com.linkedin.ugc.ShareContent"].update({
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "description": {
                        "text": text[:100]  # LinkedIn has a character limit for media descriptions
                    },
                    "media": media_asset,
                    "title": {
                        "text": title or "Shared Image"
                    }
                }]
            })

        if feed_type == "group":
            payload["containerEntity"] = f"urn:li:group:{group_id}"

        return json.dumps(payload)

    def post_content(self, payload):
        """Post content to LinkedIn"""
        try:
            response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=self.headers,
                data=payload
            )
            response.raise_for_status()
            logger.info("Successfully posted content to LinkedIn")
            return response.json()
        except Exception as e:
            logger.error(f"Error posting content: {str(e)}")
            return None
        
    def dynamic_post_creation(self):
        if 'topic' not in self.post_info:
            initial_prompt = "What's the main topic or theme of your LinkedIn post?"
            response = self.chain.predict(human_input=initial_prompt)
            self.post_info['topic'] = response.strip()

        questions_asked = 0
        while questions_asked < 3:
            next_question_prompt = f"""
            Based on the current information about the LinkedIn post:
            {json.dumps(self.post_info, indent=2)}

            What's the next most relevant question to ask the user to gather more information for a well-formed LinkedIn post?
            If you think we have enough information, respond with 'DONE'.
            """
            next_question = self.chain.predict(human_input=next_question_prompt).strip()

            if next_question.upper() == 'DONE':
                break

            key = re.sub(r'[^\w\s]', '', next_question.split()[0].lower())
            self.post_info[key] = next_question
            questions_asked += 1

        return self.generate_post_content()

    def get_next_question(self):
        if len(self.post_info) >= 4:  # Topic + 3 additional questions
            return None
        
        next_question_prompt = f"""
        Based on the current information about the LinkedIn post:
        {json.dumps(self.post_info, indent=2)}

        What's the next most relevant question to ask the user to gather more information for a well-formed LinkedIn post?
        If you think we have enough information, respond with 'DONE'.
        """
        next_question = self.chain.predict(human_input=next_question_prompt).strip()
        
        if next_question.upper() == 'DONE':
            return None
        
        return next_question

# Flask route handlers
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            flash('Please log in first.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        if access_token:
            try:
                global linkedin_automator
                linkedin_automator = LinkedinAutomate(access_token)
                user_info = linkedin_automator.get_user_info()
                
                if user_info:
                    session['access_token'] = access_token
                    session['user_info'] = user_info
                    flash('Successfully logged in!')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid access token or unable to fetch user info.')
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                flash('An error occurred during login.')
        else:
            flash('Please provide an access token.')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user_info=session.get('user_info'))

@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        topic = request.form.get('topic')
        if topic:
            try:
                linkedin_automator.post_info['topic'] = topic
                session['post_info'] = linkedin_automator.post_info
                return redirect(url_for('question_phase'))
            except Exception as e:
                logger.error(f"Error creating post: {str(e)}")
                flash('An error occurred while creating the post.')
        else:
            flash('Please provide a topic for your post.')
    
    return render_template('create_post.html')

@app.route('/question_phase', methods=['GET', 'POST'])
@login_required
def question_phase():
    if 'post_info' not in session:
        return redirect(url_for('create_post'))
    
    linkedin_automator.post_info = session['post_info']
    
    if request.method == 'POST':
        answer = request.form.get('answer')
        question = session.get('current_question')
        
        if answer == "generate me post":
            post_content = linkedin_automator.generate_post_content()
            session['post_content'] = post_content
            return redirect(url_for('preview_post'))
        
        if answer and question:
            key = re.sub(r'[^\w\s]', '', question.split()[0].lower())
            linkedin_automator.post_info[key] = answer
    
    next_question = linkedin_automator.get_next_question()
    if next_question:
        session['current_question'] = next_question
        session['post_info'] = linkedin_automator.post_info
        return render_template('question_phase.html', question=next_question)
    else:
        post_content = linkedin_automator.generate_post_content()
        session['post_content'] = post_content
        return redirect(url_for('preview_post'))


@app.route('/generate_post', methods=['GET', 'POST'])
@login_required
def generate_post():
    if 'post_info' not in session:
        return redirect(url_for('create_post'))

    linkedin_automator.post_info = session['post_info']
    post_content = linkedin_automator.generate_post_content()
    
    if post_content:
        session['post_content'] = post_content
        return redirect(url_for('preview_post'))
    else:
        flash('Error generating post content.')
        return redirect(url_for('create_post'))

@app.route('/preview_post', methods=['GET', 'POST'])
@login_required
def preview_post():
    post_content = session.get('post_content')
    if not post_content:
        flash('No post content found. Please create a new post.')
        return redirect(url_for('create_post'))

    generated_image = session.get('generated_image')
    uploaded_image = session.get('uploaded_image')

    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'generate_image':
                image_choice = request.form.get('image_choice')
                
                if image_choice == '1':  # AI Generated
                    image_prompt = linkedin_automator.generate_image_prompt(post_content)
                    if image_prompt:
                        generated_image_path = linkedin_automator.generate_image(image_prompt)
                        if generated_image_path:
                            generated_image = generated_image_path
                            session['generated_image'] = generated_image
                            uploaded_image = None
                            session.pop('uploaded_image', None)
                
                elif image_choice == '2':  # Upload from folder
                    if 'image' in request.files:
                        file = request.files['image']
                        if file and allowed_file(file.filename):
                            filename = secure_filename(file.filename)
                            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            file.save(filepath)
                            uploaded_image = filepath
                            session['uploaded_image'] = uploaded_image
                            generated_image = None
                            session.pop('generated_image', None)
                
                elif image_choice == '3':  # No image
                    generated_image = None
                    uploaded_image = None
                    session.pop('generated_image', None)
                    session.pop('uploaded_image', None)

            elif action == 'post':
                media_asset = None
                title = None
                content_type = 'text'

                if generated_image:
                    media_asset = linkedin_automator.upload_image(generated_image)
                    content_type = 'image'
                    title = "AI-generated image"
                elif uploaded_image:
                    media_asset = linkedin_automator.upload_image(uploaded_image)
                    content_type = 'image'
                    title = os.path.basename(uploaded_image)

                post_to_feed = request.form.get('post_to_feed') == 'yes'
                post_to_groups = request.form.get('post_to_groups') == 'yes'

                if post_to_feed:
                    payload = linkedin_automator.create_post_payload(
                        content_type, post_content, media_asset, title
                    )
                    if linkedin_automator.post_content(payload):
                        flash('Successfully posted to your feed!')

                if post_to_groups:
                    for group_id in linkedin_automator.python_group_list:
                        payload = linkedin_automator.create_post_payload(
                            content_type, post_content, media_asset, title, "group", group_id
                        )
                        if linkedin_automator.post_content(payload):
                            flash(f'Successfully posted to group {group_id}!')

                # Clear session data after successful post
                session.pop('post_content', None)
                session.pop('generated_image', None)
                session.pop('uploaded_image', None)

                return redirect(url_for('dashboard'))

        except Exception as e:
            logger.error(f"Error in preview_post: {str(e)}")
            flash('An error occurred while processing your request.')

    # Ensure AI-generated content starts with "Hello Connections"
    if not post_content.startswith("Hello Connections"):
        post_content = "Hello Connections,\n\n" + post_content

    return render_template('preview_post.html', 
                           post_content=post_content, 
                           generated_image=generated_image,
                           uploaded_image=uploaded_image)
@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out!')
    return redirect(url_for('home'))

@app.route('/static/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)