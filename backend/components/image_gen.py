import requests
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain

class ImagePromptBeautifier:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatGroq(
            groq_api_key="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",
            model_name="llama3-70b-8192"
        )

        # Prompt template for beautifying the image prompt
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an AI that takes user prompts and enhances them to be vivid, descriptive, and perfect for AI image generation."),
            ("human", "{human_input}")
        ])

        # Memory to maintain conversation state (not really necessary here, but included for flexibility)
        self.memory = ConversationBufferMemory(return_messages=True)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template, memory=self.memory)
        
        # Hugging Face model API details
        self.image_gen_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
        self.image_gen_headers = {
            "Authorization": "Bearer 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"
        }

    def beautify_prompt(self, user_prompt):
        """
        This function beautifies the input prompt for image generation.
        """
        try:
            beautified_prompt = self.chain.predict(human_input=user_prompt)
            return beautified_prompt.strip()
        except Exception as e:
            print(f"Error beautifying prompt: {str(e)}")
            return None

    def generate_image(self, beautified_prompt):
        """
        This function sends the beautified prompt to the Hugging Face API to generate an image.
        """
        payload = {"inputs": beautified_prompt}
        try:
            response = requests.post(self.image_gen_url, headers=self.image_gen_headers, json=payload)
            response.raise_for_status()
            with open("/Users/aswath/Desktop/ethos/ethos/backend/components/generated_image.png", "wb") as f:
                f.write(response.content)
            print("Image generated successfully and saved as 'generated_image.png'")
            return "generated_image.png"
        except requests.exceptions.RequestException as e:
            print(f"Error generating image: {e}")
            return None

    def main_func(self,query):
        """
        This function orchestrates the prompt beautification and image generation process.
        """
        user_prompt = query.strip()
        
        # Step 1: Beautify the user-provided prompt
        beautified_prompt = self.beautify_prompt(user_prompt)
        if beautified_prompt:
            print(f"Beautified Prompt: {beautified_prompt}")
            
            # Step 2: Generate image from the beautified prompt
            approval = 'yes'
            if approval == 'yes':
                self.generate_image(beautified_prompt)
            else:
                print("Image generation cancelled.")
        else:
            print("Failed to beautify the prompt.")


def image_generation(query):
    ImagePromptBeautifier().main_func(query)


# image_generation('image of a boy jumping from sky')

# import requests
# import json
# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import LLMChain

# class ImagePromptBeautifier:
#     def __init__(self):
#         # Initialize LLM
#         self.llm = ChatGroq(
#             groq_api_key="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",
#             model_name="llama3-70b-8192"
#         )

#         # Prompt template for beautifying the image prompt
#         self.prompt_template = ChatPromptTemplate.from_messages([
#             ("system", "You are an AI that takes user prompts and enhances them to be vivid, descriptive, and perfect for AI image generation."),
#             ("human", "{human_input}")
#         ])

#         # Memory to maintain conversation state (not really necessary here, but included for flexibility)
#         self.memory = ConversationBufferMemory(return_messages=True)
#         self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template, memory=self.memory)
        
#         # Hugging Face model API details
#         self.image_gen_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
#         self.image_gen_headers = {
#             "Authorization": "Bearer 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"
#         }

#     def beautify_prompt(self, user_prompt):
#         """
#         This function beautifies the input prompt for image generation.
#         """
#         try:
#             beautified_prompt = self.chain.predict(human_input=user_prompt)
#             return beautified_prompt.strip()
#         except Exception as e:
#             print(f"Error beautifying prompt: {str(e)}")
#             return None

#     def generate_image(self, beautified_prompt):
#         """
#         This function sends the beautified prompt to the Hugging Face API to generate an image.
#         """
#         payload = {"inputs": beautified_prompt}
#         try:
#             response = requests.post(self.image_gen_url, headers=self.image_gen_headers, json=payload)
#             response.raise_for_status()
#             with open("generated_image.png", "wb") as f:
#                 f.write(response.content)
#             print("Image generated successfully and saved as 'generated_image.png'")
#             return "generated_image.png"
#         except requests.exceptions.RequestException as e:
#             print(f"Error generating image: {e}")
#             return None

#     def main_func(self):
#         """
#         This function orchestrates the prompt beautification and image generation process.
#         """
#         user_prompt = input("Please enter the prompt for the image you want to generate: ").strip()
        
#         # Step 1: Beautify the user-provided prompt
#         beautified_prompt = self.beautify_prompt(user_prompt)
#         if beautified_prompt:
#             print(f"Beautified Prompt: {beautified_prompt}")
            
#             # Step 2: Generate image from the beautified prompt
#             approval = input("Do you approve this beautified prompt for image generation? (yes/no): ").strip().lower()
#             if approval == 'yes':
#                 self.generate_image(beautified_prompt)
#             else:
#                 print("Image generation cancelled.")
#         else:
#             print("Failed to beautify the prompt.")


# if __name__ == "__main__":
#     ImagePromptBeautifier().main_func()
