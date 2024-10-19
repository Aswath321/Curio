#Github
import getpass
import os
import os
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote_plus
import requests
from urllib.parse import quote_plus, urljoin
import base64
from dotenv import load_dotenv

#load env variables
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

#to extract functionality required
prompt_template2 = """
You are an assistant for GitHub. The user can perform one of the following actions based on their request:

1) Create a new repository: Respond with 'create_repo repo_name'.
2) Search for a repository in the user's account: Respond with 'search_my_repos repo_name'.
3) Search for a repository in all of GitHub: Respond with 'search_all_repos repo_name'.
4) Upload a file to a specific repository: Respond with 'upload_file repo_name file_path'.

Please analyze the user's request: "{query}" and determine the desired action. Provide a clear response based on the identified action.

Response (Choose one of the following formats):
- 'create_repo repo_name '
- 'search_my_repos repo_name '
- 'search_all_repos repo_name '
- 'upload_file repo_name file_path '
"""



class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_repo(self, name, private=False, has_issues=True, has_projects=True, has_wiki=True):
        url = f"{self.base_url}/user/repos"
        data = {
            "name": name,
            "description": "from chat",
            "private": private,
            "has_issues": has_issues,
            "has_projects": has_projects,
            "has_wiki": has_wiki
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def search_my_repos(self, query, sort="updated", order="desc"):
        url = f"{self.base_url}/user/repos"
        params = {"q": query, "sort": sort, "order": order}
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def search_all_repos(self, query, sort="stars", order="desc"):
        url = f"{self.base_url}/search/repositories"
        params = {"q": query, "sort": sort, "order": order}
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def upload_file(self, repo_name, file_path, commit_message="Adding a new file via API"):
        # Read the file content
        with open(file_path, "rb") as file:
            content = base64.b64encode(file.read()).decode("utf-8")

        # Extract the file name from the file path
        file_name = os.path.basename(file_path)

        # Prepare the API URL for the file path in the repository
        url = f"{self.base_url}/repos/{self.get_authenticated_user()}/{repo_name}/contents/{file_name}"

        data = {
            "message": commit_message,
            "content": content
        }

        # Send the PUT request to upload the file
        response = requests.put(url, json=data, headers=self.headers)

        if response.status_code == 201:
            print(f"File '{file_path}' uploaded successfully.")
            print(f"View file at: {response.json()['content']['html_url']}")
        else:
            print(f"Failed to upload file. Status code: {response.status_code}")
            print(response.json())

    def get_authenticated_user(self):
        url = f"{self.base_url}/user"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['login']
        else:
            raise Exception("Failed to fetch authenticated user info.")

def parse(prompt):
    prompt = prompt_template2.format(query=prompt)
    response = model.generate_content(prompt)
    # print(response.text)
    return response.text

def github_action(user_prompt):
    print("w",user_prompt,"y")
    #GITHUB - TOKEN
    token = os.getenv("GITHUB_TOKEN")
    github = GitHubAPI(token)

    action = parse(user_prompt)
    # print("1",action)

    if "create_repo" in action:
        repo_name = action.split('create_repo ')[1]
        private = "private" in user_prompt
        repo = github.create_repo(repo_name, private)
        print(repo)
        return(f"Created new repo: {repo['name']}\n\nRepo URL: {repo['html_url']}")

    elif "search_my_repos" in action:
        repo_name = action.split('search_my_repos ')[1]
        repos = github.search_my_repos(repo_name)
        l=[]
        l.append(f"Found {len(repos)} of your repos matching '{repo_name}':\n\n")
        for repo in repos[:5]:
            l.append(f"- {repo['name']}: {repo['html_url']}")
        return " ".join(l)

    elif "search_all_repos" in action:
        repo_name = action.split('search_all_repos ')[1]
        repos = github.search_all_repos(repo_name)
        l=[]
        l.append(f"Found {len(repos['items'])} public repos matching '{repo_name}':\n\n")
        for repo in repos['items'][:5]:
            l.append(f"- {repo['full_name']}: {repo['html_url']}]\n")
        return " ".join(l)

    elif "upload_file" in action:
        parts = action.split('upload_file ')[1]
        repo_name, file_path = parts.split(" ")[0], parts.split(" ")[1]
        file_path=file_path[:-1]
        github.upload_file(repo_name, file_path)
        return(f"Uploaded file to {repo_name}")
    else:
        return("Sorry, I couldn't understand your request. Please try again.")


# print(github_action("create a new github repo called test2"))
#other functionalities will be added in the next iteration