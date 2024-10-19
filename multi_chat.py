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
        ("system", "You are an AI assistant named Curio in a multi-user chat application.You helo resolve user queries in near real time"),
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
    room_id = str(uuid.uuid4())  # Generate a unique room ID
    session['username'] = username
    session['room'] = room_id

    # Create the room and generate a shareable link
    room_link = request.host_url + 'chat/' + room_id
    return render_template('chat.html', room=room_id, username=username, room_link=room_link)

# Route for joining a room (by pasting link or entering details manually)
@app.route('/join_room', methods=['POST'])
def join_room_route():
    # Check if the user pasted a link
    room_link = request.form.get('room_link')
    username = request.form.get('username')

    if room_link:
        # Extract room ID from the link
        room_id = room_link.split('/')[-1]
    else:
        # Manually entered room ID
        room_id = request.form.get('room_id')

    session['username'] = username
    session['room'] = room_id

    return redirect(url_for('chat_room', room_id=room_id))

# Route for chat room
@app.route('/chat/<room_id>')
def chat_room(room_id):
    username = session.get('username')
    if not username:
        # If no username, redirect to ask for it
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
    username = session.get('username')
    room = session.get('room')
    leave_room(room)
    
    if room in rooms and username in rooms[room]:
        rooms[room].remove(username)
        if not rooms[room]:
            del rooms[room]
    
    emit('status', {'message': f'{username} has left the room.'}, room=room)
    emit('update_users', {'users': list(rooms.get(room, []))}, room=room)

@socketio.on('message')
def handle_message(data):
    message = data['message']
    room = session.get('room')
    username = session.get('username')

    # Wrap username in <strong> tags to make it bold
    emit('message', {'username': f"{username}", 'message': message}, room=room)

    # Check if the message starts with "@curio"
    if message.strip().lower().startswith("@curio"):
        # Remove the "@curio" prefix and get AI response
        ai_query = message.strip()[6:].strip()  # "@curio" is 6 characters long
        ai_response = asyncio.run(process_ai_message(ai_query))
        emit('message', {'username': 'Curio', 'message': ai_response}, room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
