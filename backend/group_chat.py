from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import asyncio
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize the Llama3-70B model with Groq
llm = ChatGroq(
    groq_api_key="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",
    model_name="llama3-70b-8192"
)

# Define the conversation prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI assistant in a multi-user chat application."),
        ("human", "{input}")
    ]
)

# Chain the prompt template with the Llama model
chain = prompt_template | llm

# Store active rooms and their users
rooms = {}

# Route for the home page (room creation or joining)
@app.route('/')
def index():
    return render_template('index.html')

# Route for creating a new room (group)
@app.route('/create_room', methods=['POST'])
def create_room():
    username = request.form.get('username')
    room_number = len(rooms) + 1  # Generate room number (r1, r2, ...)
    room_id = f'r{room_number}'  # Format: r1, r2, ...
    
    session['username'] = username
    session['room'] = room_id

    # Create the room and generate a shareable link
    room_link = request.host_url + 'chat/' + room_id
    return render_template('chat.html', room=room_id, username=username, room_link=room_link)

# Route for joining a room (by pasting link or entering details manually)
@app.route('/join_room', methods=['POST'])
def join_room_route():
    room_link = request.form.get('room_link')
    username = request.form.get('username')

    if room_link:
        # Extract room ID from the link
        room_id = room_link.split('/')[-1]
    else:
        room_id = request.form.get('room_id')

    session['username'] = username
    session['room'] = room_id

    return redirect(url_for('chat_room', room_id=room_id))

# Route for chat room
@app.route('/chat/<room_id>')
def chat_room(room_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('ask_username', room_id=room_id))
    
    session['room'] = room_id
    return render_template('chat.html', room=room_id, username=username)

# Ask username if only room ID is provided (used if no session)
@app.route('/ask_username/<room_id>', methods=['GET', 'POST'])
def ask_username(room_id):
    if request.method == 'POST':
        username = request.form.get('username')
        session['username'] = username
        return redirect(url_for('chat_room', room_id=room_id))
    return render_template('ask_username.html', room_id=room_id)

# Asynchronous function to process the AI's response
async def process_ai_message(message):
    try:
        response = await asyncio.to_thread(
            lambda: chain.invoke({"input": message})
        )
        return response.content
    except Exception as e:
        return f"Error: {str(e)}"

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    
    if room not in rooms:
        rooms[room] = set()
    rooms[room].add(username)
    
    emit('status', {'message': f'{username} has joined the room.'}, room=room)
    emit('update_users', {'users': list(rooms[room])}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    
    if room in rooms:
        rooms[room].discard(username)
        emit('status', {'message': f'{username} has left the room.'}, room=room)
        emit('update_users', {'users': list(rooms[room])}, room=room)

@socketio.on('message')
def handle_message(data):
    message = data['message']
    username = session.get('username')
    room = session.get('room')

    # Emit the user's message to the chat room
    emit('message', {'username': username, 'message': message}, room=room)

    # Check if the message starts with "@ai"
    if message.strip().lower().startswith('@ai'):
        # Remove the "@ai" prefix and get the AI query
        ai_query = message.strip()[4:].strip()  # Adjusted to 4 to account for "@ai "
        
        # Process AI response asynchronously
        asyncio.run(handle_ai_response(ai_query, room))

async def handle_ai_response(user_query, room):
    try:
        # Get AI's response
        ai_response = await process_ai_message(user_query)
        
        # Emit AI's response back to the chat room
        emit('message', {'username': 'AI', 'message': ai_response}, room=room)
    except Exception as e:
        # Handle errors and emit an error message
        emit('message', {'username': 'AI', 'message': f"Error: {str(e)}"}, room=room)


# Error handling for room not found
@app.errorhandler(404)
def not_found(e):
    return "Room not found. Please check the link and try again.", 404

if _name_ == '_main_':
    socketio.run(app, debug=True)