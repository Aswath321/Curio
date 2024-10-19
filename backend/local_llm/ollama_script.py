import subprocess
import time

def start_ollama():
    try:
        ollama_process = subprocess.Popen(["ollama", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Ollama is starting")
        time.sleep(5)  
        return ollama_process
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return None

def stop_ollama(ollama_process):
    if ollama_process:
        ollama_process.terminate()
        print("Ollama service stopped.")

def handle_conversation(query,ollama_process):
    context=""
    
    user_input=query
    formatted_prompt = template.format(context=context, question=user_input)
    response = subprocess.run(
        ["ollama", "run", "llama3.1", formatted_prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if response.returncode!=0:
        print("Error running Ollama:", response.stderr)

    context +=f"\nUser: {user_input}\nBot:{response.stdout.strip()}"
    stop_ollama(ollama_process)
    
    # print("Bot:", response.stdout.strip())
    return response.stdout.strip()
    


template = """
Answer the user question based on the previous context if there is any by taking relevant information alone, else answer normally.

Context:{context}

Question : {question}

Answer : 
"""


def initialisation(query):
    ollama_process = start_ollama()
    # if ollama_process:
    return handle_conversation(query,ollama_process)
    # return "process didn't start"
    # stop_ollama(ollama_process)

# print(initialisation("pytho code to print fibonacci numbers?"))

# if __name__ == "__main__":
#     ollama_process = start_ollama()
#     if ollama_process:
#         try:
#             handle_conversation()
#         finally:
#             stop_ollama(ollama_process)
