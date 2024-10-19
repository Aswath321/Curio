# g
# import sqlite3

# def setup_database():
#     connection = sqlite3.connect("chat.db")
#     cursor = connection.cursor()
    
#     # Create the 'chats' table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS chats (
#             id TEXT PRIMARY KEY,
#             messages TEXT
#         )
#     """)
    
#     # Create the 'messages' table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS messages (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             chat_id TEXT,
#             text TEXT,
#             sender TEXT,
#             FOREIGN KEY(chat_id) REFERENCES chats(id)
#         )
#     """)

#     connection.commit()
#     connection.close()

# if __name__ == "__main__":
#     setup_database()

import sqlite3

def setup_database():
    connection = sqlite3.connect("chat1.db")
    cursor = connection.cursor()
    
    # Create the 'chats' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL
        )
    """)
    
    # Create the 'messages' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            text TEXT,
            sender TEXT,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_knowledge_graphs (
            user_id TEXT PRIMARY KEY,
            graph_data TEXT NOT NULL
        )
    """)

    cursor.execute("""
    ALTER TABLE chats ADD COLUMN llm_type TEXT DEFAULT 'api'
    """)

    # cursor.execute("""
    # ALTER TABLE chats drop COLUMN type
    # """)



    
    connection.commit()
    connection.close()

# def migrate_database():
#     connection = sqlite3.connect("chat.db")
#     cursor = connection.cursor()

#     # Check if user_id column exists in chats table
#     cursor.execute("PRAGMA table_info(chats)")
#     columns = [column[1] for column in cursor.fetchall()]
    
#     if "user_id" not in columns:
#         # Add user_id column to existing chats table
#         cursor.execute("ALTER TABLE chats ADD COLUMN user_id TEXT")
        
#         # You might want to set a default user_id for existing chats
#         # This is just an example, adjust as needed
#         cursor.execute("UPDATE chats SET user_id = 'default_user' WHERE user_id IS NULL")

        
#     connection.commit()
#     connection.close()


if __name__ == "__main__":
    setup_database()
    # migrate_database()




#  CREATE TABLE IF NOT EXISTS flashcards (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         chat_id TEXT,
#         question TEXT,
#         answer TEXT
#     )