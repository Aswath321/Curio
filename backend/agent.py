import google.generativeai as genai
import re
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel
import json
from typing import List, Dict
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import time
from pprint import pprint
import os
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from components.student_progress import progress
load_dotenv()
from components.youtube import youtube_function
import chromadb
from chromadb.utils import embedding_functions
from chromadb.config import Settings
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from PIL import Image
import io
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import google.generativeai as genai
import os
import google.generativeai as genai
from typing import Dict, Any
import json
import warnings
from langchain_community.chat_message_histories import ChatMessageHistory
import vertexai
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_google_vertexai import VertexAI
import asyncio
import typing
from components.amazon_scrape import scrape_amazon
from components.whatsapp import whatsapp_message
from components.gmail import call_mail
from components.calender import schedule_calender
from components.rem import schedule_reminder
from components.image import get_description
from components.recipe import get_recipes
from components.github import github_action
from components.news import get_news
# from components.web_scraper import web_scrape
import networkx as nx
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import io
import networkx as nx
from typing import Dict, List, Any
import spacy
from collections import Counter
import firebase_admin
from firebase_admin import credentials, auth
from local_llm.ollama_script import initialisation
from langchain_groq import ChatGroq
import subprocess
from components.recommendation import process_recommendation_request
from components.image_gen import image_generation





import subprocess
def run_external_script():
    try:
        process = subprocess.run(
            ["python3", "/Users/aswath/Desktop/ethos/ethos/backend/components/web_scraper.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if process.returncode == 0:
            print(f"External script output:\n{process.stdout}")
        else:
            print(f"External script error:\n{process.stderr}")
    except Exception as e:
        print(f"Error running the external script: {e}")\

run_external_script()



genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))  
model = genai.GenerativeModel('gemini-1.5-flash')
memory = ConversationBufferMemory()


chroma_client = chromadb.Client(Settings(allow_reset=True))

PERSISTENCE_DIRECTORY = "./chroma_persistence"

chroma_client = chromadb.PersistentClient(path=PERSISTENCE_DIRECTORY)
collection = chroma_client.get_or_create_collection(
    name="message_history",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
)


collection = chroma_client.get_or_create_collection(name="message_history")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def get_db_connection1():
    connection = sqlite3.connect("chat2.db")
    connection.row_factory = sqlite3.Row
    return connection
from pydantic import BaseModel
import json
import re
from google.generativeai import types as genai_types

class AgentRes(BaseModel):
    tool_name: str
    tool_input: dict
    tool_output: str | None = None
    
   
    @classmethod
    def from_gemini(cls, res: genai_types.GenerateContentResponse, user_q: str):
        try:
            if not res.candidates:
                raise ValueError("No candidates in the response")

            if res.candidates[0].finish_reason == "SAFETY":
                safety_ratings = res.candidates[0].safety_ratings
                blocked_categories = [rating.category for rating in safety_ratings if rating.probability != "NEGLIGIBLE"]
                raise ValueError(f"Response blocked due to safety concerns: {', '.join(blocked_categories)}")

            text = res.text
            text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
            
            try:
                out = json.loads(text)
            except json.JSONDecodeError:
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    json_str = match.group(0)
                    try:
                        out = json.loads(json_str)
                    except json.JSONDecodeError:
                        # If JSON parsing still fails, treat the entire text as the final answer
                        out = {"name": "final_answer", "parameters": {"text": text}}
                else:
                    # If no JSON-like structure is found, treat the entire text as the final answer
                    out = {"name": "final_answer", "parameters": {"text": text}}

            agent_res = cls(tool_name=out["name"], tool_input=out["parameters"])
            if agent_res.tool_name != "final_answer":
                agent_res.tool_input['text'] = user_q

            return agent_res
        except Exception as e:
            print(f"Error processing Gemini response: {str(e)}")
            print(f"Response details:\n{res}")
            # Fallback to a default response
            return cls(tool_name="final_answer", tool_input={"text": f"I apologize, but I encountered an error processing your request: {str(e)}. Could you please rephrase your question or try again later?"})


class State(typing.TypedDict):
    user_q: str
    chat_history: list 
    lst_res: list[AgentRes]
    output: dict


@tool("tool_browser")
def tool_browser(q: str) -> str:
    """Search on DuckDuckGo browser by passing the input `q`"""
    return DuckDuckGoSearchRun().run(q)

@tool("final_answer")
def final_answer(text: str) -> str:
    """Returns a natural language response to the user by passing the input `text`. 
    """
    return text




@tool("youtube")
def youtube(text:str)->str:
    """Returns a summary of the given youtube video,or creates a transcript or searches youtube for the given video content and fetches thr url
    """
    return youtube_function(text)


@tool("amazon")
def amazon(text:str)->str:
    """Returns a summary of the given product by scraping the relevant information from amazon"""
    return scrape_amazon(text)


@tool("whatsapp")
def whatsapp(text:str)->str:
    """Sends a whatsapp message to the user given the content"""
    return whatsapp_message(text)

@tool("gmail")
def gmail(text:str)->str:
    """Given a user id and content send a gmail and also to retreive mails based on content given"""
    return call_mail(text)

@tool("calender")
def calender(text:str)->str:
    """Schedule meetings/events in calenders and also view the meetings/events from the calender"""
    return schedule_calender(text)

@tool("reminder")
def reminder(text:str)->str:
    """Set reminders for user with priority levels"""
    return schedule_reminder(text)

@tool("image")
def image(text:str)->str:
    """Given an image link with soem content regarding it, idenitfy the content and return it"""
    return get_description(text)

@tool("recipe")
def recipe(text:str)->str:
    """Given a dish, search the recipies and get it"""
    return get_recipes(text)



@tool("github")
def github(text:str)->str:
    """Add a repo, delete a repo, add files to repo and other github actions"""
    return github_action(text)

@tool("news")
def news(text:str)->str:
    """Based on the user's choice get them the news from news articles"""
    return get_news(text)

@tool("web_scrape")
def web_scrape(text:str)->str:
    """Web scrape and retrieve relvant content for the user"""
    with open('/Users/aswath/Desktop/ethos/ethos/backend/components/web_scrape_content.txt','w') as f:
        f.write(text)
    run_external_script()
    with open("/Users/aswath/Desktop/ethos/ethos/backend/components/agent_res.txt", "r") as f:
        result = f.read()
    print(result)
    return result


@tool("student_progress")
def student_progress(text:str)->str:
    """get the progress and analysis of any given student"""
    return progress(text)

@tool("recommend_project")
def recommend_project(text:str)->str:
    """Based on the student's skills and interests, recommend projects to the students"""
    return process_recommendation_request(text)

@tool("image_generation")
def image_generation(text:str)->str:
    """Based on the user's quey they will give a prompt for which you have to generate an image"""
    return process_recommendation_request(text)

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.nlp = spacy.load("en_core_web_sm")

    def add_node(self, entity: str, attributes: Dict[str, Any] = None):
        if attributes is None:
            attributes = {}
        self.graph.add_node(entity, **attributes)

    def add_edge(self, entity1: str, entity2: str, relationship: str = None):
        self.graph.add_edge(entity1, entity2, relationship=relationship)

    def update_from_text(self, text: str):
        doc = self.nlp(text)
        entities = [ent.text.lower() for ent in doc.ents]
        for entity in entities:
            self.add_node(entity)
        
        for i in range(len(entities) - 1):
            self.add_edge(entities[i], entities[i+1])

    def get_related_entities(self, entity: str, depth: int = 2) -> List[str]:
        if entity not in self.graph:
            return []
        
        related = set()
        for node in nx.bfs_tree(self.graph, entity, depth_limit=depth):
            related.add(node)
        
        return list(related)

    def get_most_relevant_entities(self, text: str, n: int = 5) -> List[str]:
        doc = self.nlp(text)
        text_entities = [ent.text.lower() for ent in doc.ents]
        
        all_related = []
        for entity in text_entities:
            all_related.extend(self.get_related_entities(entity))
        
        entity_counts = Counter(all_related)
        return [entity for entity, _ in entity_counts.most_common(n)]

    def visualize(self, query: str, output_dir: str = "graph_visualizations"):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        
        # Draw all nodes and edges
        nx.draw(self.graph, pos, node_color='lightblue', with_labels=True, node_size=1000, font_size=8)
        
        # Highlight nodes related to the current query
        related_entities = self.get_most_relevant_entities(query)
        nx.draw_networkx_nodes(self.graph, pos, nodelist=related_entities, node_color='red', node_size=1500)
        
        # Add edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'relationship')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        
        plt.title(f"Knowledge Graph for Query: {query}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = 1
        filename = f"knowledge_graph_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath)
        plt.close()
        
        return filepath
    def serialize(self):
        return nx.node_link_data(self.graph)

    @classmethod
    def deserialize(cls, data):
        kg = cls()
        kg.graph = nx.node_link_graph(data)
        return kg



class AIAgent:
    def __init__(self):
        self.functions: Dict[str, str] = {
            "amazon_scrape": "Scrape product information from Amazon",
            "whatsapp_message": "Send a WhatsApp message",
            "gmail": "Perform Gmail-related tasks",
            "calendar": "Schedule events in the calendar",
            "reminder": "Set reminders and view reminders with priority and description",
            "image_description": "Analyze and describe images",
            "recipe": "Find and provide recipes",
            "pdf_chat": "Chat with PDF content using a rag created on pdf files in a directory that the user provides",
            "youtube": "Interact with YouTube content",
            "github":"add repos, browse local and global repos",
            "news":"get latest news from different categories based on request",
            "normal_prompt":"getting normal prompt response from gemini when there is no need of other functions",
            "web_search":"for situations where simple reply from llm is not enough and web search is required"
        }
        self.usage_history: Dict[str, int] = {func: 0 for func in self.functions}
        self.learning_data: Dict[str, Any] = {}
        #identity for agent
        self.identity = {
            "name": "Curio",
            "personality": "friendly and knowledgeable AI assistant that can analyse user queries and perform respective actions making their everyday tasks easier.You can do scraping,searching,sending whatsapp messages,mails,setting meetings in calenders,adding reminders, pdf,image and video answering,getting latets news,creating and modifyig and searching github repos,finding best recipes,post linkedin content and a lot more",
            "background": "Created by a team of AI enthusiasts to help with various tasks and queries and make the life of user easy"
        }
        self.knowledge_graph = KnowledgeGraph()
        self.initialize_chroma_db()
        self.used_tools = set()
        self.workflow_state = {"used_tools": set()} 
        # self.tool_results = {} 

    def initialize_chroma_db(self):
        if not os.path.exists(PERSISTENCE_DIRECTORY):
            os.makedirs(PERSISTENCE_DIRECTORY)
        print(f"Chroma DB initialized. Persistence directory: {PERSISTENCE_DIRECTORY}")
        # print(f"Current message count: {collection.count()}")

    def store_message(self, role: str, content: str):
        try:
            collection.add(
                documents=[content],
                metadatas=[{"role": role}],
                ids=[f"{role}_{collection.count() + 1}"]
            )
            # print(f"Message stored. New count: {collection.count()}")
            # print(f"Stored message - Role: {role}, Content: {content[:50]}...")
            self.knowledge_graph.update_from_text(content)
        except Exception as e:
            print(f"Error storing message: {e}")

    def get_relevant_messages(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        # print(f"Attempting to retrieve relevant messages for query: {query}")
        # print(f"Current message count: {collection.count()}")

        if collection.count() == 0:
            print("No messages in the collection.")
            return []

        try:
            results = collection.query(
                query_texts=[query],
                n_results=min(k, collection.count())
            )

            relevant_messages = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    relevant_messages.append({
                        "role": results['metadatas'][0][i]['role'],
                        "content": doc
                    })
            
           
            
            return relevant_messages
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            return []


    def save_knowledge_graph(self, user_id):
        conn = get_db_connection1()
        cursor = conn.cursor()
        
        graph_data = json.dumps(self.knowledge_graph.serialize())
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_knowledge_graphs (user_id, graph_data)
            VALUES (?, ?)
        """, (user_id, graph_data))
        
        conn.commit()
        conn.close()

    def load_knowledge_graph(self, user_id):
        conn = get_db_connection1()
        cursor = conn.cursor()
        
        cursor.execute("SELECT graph_data FROM user_knowledge_graphs WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            graph_data = json.loads(result[0])
            self.knowledge_graph = KnowledgeGraph.deserialize(graph_data)
        else:
            self.knowledge_graph = KnowledgeGraph()

    

    
    dic_tools = {
            "tool_browser": tool_browser,
            "final_answer": final_answer,
            "youtube": youtube,
            "amazon":amazon,
            "whatsapp":whatsapp,
            "gmail":gmail,
            "calender":calender,
            "reminder":reminder,
            "github": github,
            "news": news,
            "image": image, 
            "recipe": recipe,
            "web_scrape": web_scrape,
            "student_progress":student_progress,
            "recommend_project":recommend_project,
            "image_generation":image_generation
            
        }
    str_tools = "\n".join([f"{n+1}. `{v.name}`: {v.description}" for n, v in enumerate(dic_tools.values())])

    prompt_tools = f"You can use the following tools:\n{str_tools}"

    def get_prompt(self):
        prompt = f"""
            You are {self.identity['name']}, a {self.identity['personality']}. {self.identity['background']}
            You can use the following tools:
            {self.prompt_tools}

            Your goal is to provide the user with the best possible answer, including key information about the sources and tools used.

            Note, when using a tool, you provide the tool name and the arguments to use in JSON format. 
            

            For each call, you MUST ONLY use one tool AND the response format must ALWAYS be in the pattern:
            ```json
            {{"name":"<tool_name>", "parameters": {{"<tool_input_key>":<tool_input_value>}}}}
            ```
            Remember, do NOT use any tool with the same query more than once.
            Remember, if the user doesn't ask a specific question, you MUST use the `final_answer` tool directly.

            Every time the user asks a question, you take note of some keywords in the memory.
            Every time you find some information related to the user's question, you take note of some keywords in the memory.

            You should aim to collect information from a diverse range of sources before providing the answer to the user. 
            Once you have collected plenty of information to answer the user's question use the `final_answer` tool.

            What is very important and strictly be followed is don't use  same tool more than once
            """

       

        return prompt

    def save_memory(self, lst_res: List[AgentRes], user_q: str) -> List[Dict[str, str]]:
        memory = []
        for res in [res for res in lst_res if res.tool_output is not None]:
            memory.extend([
                {"role": "assistant", "content": json.dumps({"name": res.tool_name, "parameters": res.tool_input})},
                {"role": "user", "content": res.tool_output}
            ])
            # Add tool results to the memory
            memory.append({"role": "system", "content": f"{res.tool_name} result: {res.tool_output}"})
        
        if memory:
            memory += [{"role": "user", "content": f'''
                    This is just a reminder that my original query was `{user_q}`.
                    Only answer to the original query, and nothing else, but use the information I gave you. 
                    Provide as much information as possible when you use the `final_answer` tool.
                    '''}]

        return memory

    def run_agent(self,user_q: str, chat_history: List[Dict[str, str]], lst_res: List[AgentRes], lst_tools: List[str],prompt="",dic_tools={}) -> AgentRes:
        memory = self.save_memory(lst_res=lst_res, user_q=user_q)
        # memory.extend([{"role": "system", "content": f"Relevant past information: {mem}"} for mem in relevant_memories])
        prompt=self.get_prompt()
        self.store_message("user", user_q)
        # print(prompt)
        relevant_messages = self.get_relevant_messages(user_q)
        kg_context = self.get_knowledge_graph_context(user_q)
        # print("\n\nKG CONTEXT",kg_context,"\n\n")
        # print(f"Number of relevant messages: {len(relevant_messages)}")
        # for msg in relevant_messages:
        #     print(f"Relevant message - Role: {msg['role']}, Content: {msg['content'][:50]}...")

        if memory:
            tools_used = [res.tool_name for res in lst_res]
            if len(tools_used) >= len(lst_tools):
                memory[-1]["content"] = "You must now use the `final_answer` tool."
        
        # messages = [
        #     {"role": "system", "content": prompt + "\n" + self.prompt_tools},
        #     # *chat_history,
        #     *relevant_messages,
        #     {"role": "user", "content": user_q},
        #     *memory
        # ]
        # print(messages)
        # pprint(messages)

        context_summary = self.summarize_context(chat_history, relevant_messages)

        # print(chat_history)

        messages = [
                {"role": "system", "content": prompt + "\n" + self.prompt_tools},
                {"role": "system", "content": f"Knowledge Graph Context: {kg_context}"},
                *chat_history,
                # *relevant_messages,
                {"role": "user", "content": user_q},
                *memory
            ]

        # messages.insert(1, {
        # "role": "system", 
        # "content": "Carefully consider the user's query and select the most appropriate tool based on the detailed descriptions provided. If unsure, use the tool_browser or final_answer tool."
        # })
        # print("\nmessages:",messages,"\n")
        
        graph_image_path = self.knowledge_graph.visualize(user_q)

        # identity_prompt = "You are a helpful assistant."
        
        full_prompt = '\n'.join([f"{m['role']}: {m['content']}" for m in messages])
        response = model.generate_content(full_prompt)
        # response=conversation.predict(input=full_prom pt)
        response.graph_visualization = graph_image_path
        agent_res = AgentRes.from_gemini(response, user_q)

        if agent_res.tool_name == "final_answer":
            self.store_message("assistant", agent_res.tool_input['text'])
        else:
            self.store_message("assistant", f"Using tool: {agent_res.tool_name}")
        return agent_res


    

    def get_knowledge_graph_context(self, query: str) -> str:
        relevant_entities = self.knowledge_graph.get_most_relevant_entities(query)
        context = "Based on the user's history and preferences, consider the following relevant concepts: "
        context += ", ".join(relevant_entities)
        return context

    def summarize_context(self, chat_history: List[Dict[str, str]], relevant_messages: List[Dict[str, str]]) -> str:
        recent_history = chat_history[-3:]  # Consider last 3 messages from chat history
        summary = "Recent conversation: "
        for msg in recent_history:
            summary += f"{msg['role']}: {msg['content'][:50]}... "
        
        summary += "\nRelevant past information: "
        for msg in relevant_messages[:2]:  
            summary += f"{msg['content'][:50]}... "
        
        return summary

    def node_agent(self, state):
        print("--- node_agent ---")
        agent_res = self.run_agent(prompt="", 
                            dic_tools={k:v for k,v in self.dic_tools.items() if k not in self.used_tools},
                            user_q=state["user_q"], 
                            chat_history=state["chat_history"], 
                            lst_res=state["lst_res"],
                            lst_tools=[k for k in self.dic_tools.keys() if k not in self.used_tools])
        
        return {"lst_res": [agent_res]}

    def conditional_edges(self, state):
        print("--- conditional_edges ---")
        last_res = state["lst_res"][-1]
        next_node = last_res.tool_name if isinstance(state["lst_res"], list) else "final_answer"
        
        # Check if the next_node exists in the workflow
        if next_node in self.dic_tools:
            self.used_tools.add(next_node)
            self.workflow_state["used_tools"].add(next_node)
            print("Tool added, current used tools:", self.used_tools)
            print("next_node:", next_node)
            return next_node
        else:
            print(f"Tool {next_node} not found in workflow. Defaulting to final_answer.")
            return "final_answer"

    

    def node_tool(self, state):
        print("--- node_tool ---")
        res = state["lst_res"][-1]
        print(f"{res.tool_name}(input={res.tool_input})")  
        
        if res.tool_name not in self.dic_tools:
            print(f"Tool {res.tool_name} not found. Returning final answer.")
            return {"output": AgentRes(tool_name="final_answer", 
                                    tool_input=res.tool_input, 
                                    tool_output="I apologize, but I don't have access to that functionality right now.")}
        
        tool_output = str(self.dic_tools[res.tool_name](res.tool_input))
        agent_res = AgentRes(tool_name=res.tool_name, 
                            tool_input=res.tool_input, 
                            tool_output=tool_output)
        
        return {"output": agent_res} if res.tool_name == "final_answer" else {"lst_res": [agent_res]}




    def get_workflow(self):

        workflow = StateGraph(State)



        ## add Agent node
        workflow.add_node(node="Agent", action=self.node_agent) 
        workflow.set_entry_point(key="Agent")  

        ## add Tools nodes
        for k in self.dic_tools.keys():
            workflow.add_node(node=k, action=self.node_tool)

        ## conditional_edges from Agent
        workflow.add_conditional_edges(source="Agent", path=self.conditional_edges)

         ## normal_edges to Agent

        for k in self.dic_tools.keys():
            if k != "final_answer":
                workflow.add_edge(start_key=k, end_key="Agent")
        ## end the graph
        workflow.add_edge(start_key="final_answer", end_key=END)
        g = workflow.compile()
        print("1....",self.workflow_state["used_tools"],"......1")
        image_data = g.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
        image = Image.open(io.BytesIO(image_data))
        image.save("output_image.png")

        return g

