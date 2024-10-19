import os
from langchain_groq import ChatGroq
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

class StudentQueryProcessor:
    def __init__(self):
        # Initialize Groq chat with API key
        self.groq_api_key = os.environ['GROQ_API_KEY']
        self.llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name="llama3-70b-8192",
            temperature=0.2
        )
    
    def extract_student_id(self, query: str) -> Optional[str]:
        """Extract student ID using LLM instead of regex."""
        extraction_prompt = f"""
        Extract the student ID from the following query. 
        - Student IDs start with 'S' or 'SI' followed by numbers
        - Return ONLY the ID in uppercase, nothing else
        - If no valid student ID is found, return 'NONE'
        
        Query: {query}
        
        ID:"""
        
        try:
            response = self.llm.invoke(extraction_prompt)
            extracted_id = response.content.strip()
            return None if extracted_id == 'NONE' else extracted_id
            
        except Exception as e:
            print(f"Error extracting student ID: {str(e)}")
            return None
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process the query and return structured response."""
        # Extract student ID using LLM
        student_id = self.extract_student_id(query)
        
        if not student_id:
            return {
                "success": False,
                "error": "No valid student ID found in query",
                "query": query
            }
        
        # Create a structured prompt for analyzing the query
        analysis_prompt = f"""
        Analyze the following student-related query and provide structured information.
        
        Query: {query}
        Student ID: {student_id}
        
        Provide a JSON response with the following structure:
        {{
            "request_type": "<type of request (e.g., details, grades, attendance)>",
            "specific_information": "<what specific information is being requested>",
            "additional_context": "<any other relevant details from the query>"
        }}
        
        Response:"""
        
        try:
            # Get response from Groq
            response = self.llm.invoke(analysis_prompt)
            
            return {
                "success": True,
                "student_id": student_id,
                "original_query": query,
                "processed_response": response.content,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "student_id": student_id,
                "query": query
            }

    def get_student_details(self, query: str) -> str:
        """Main interface method for getting student details."""
        result = self.process_query(query)
        
        if not result["success"]:
            return f"Error processing query: {result.get('error', 'Unknown error')}"
            
        return result["processed_response"]


# Example usage
def progress(query):
    processor = StudentQueryProcessor()
    
    # Test queries
    # test_queries = [
    #     "give me the details about the student SI101",
    #     "what are the grades for student si203?",
    #     "show attendance record for S303",
    #     "can you tell me about the performance of student SI405 in the last semester",
    #     "invalid query without any student ID"
    # ]
    
    # for query in test_queries:
    #     print("\nQuery:", query)
    #     # First show the extracted ID
    #     student_id = processor.extract_student_id(query)
    #     print("Extracted ID:", student_id)
    #     # Then show the full processed response
    #     response = processor.get_student_details(query)
    #     print("Full Response:", response)
    #     print("-" * 50)
    student_id = processor.extract_student_id(query)
    print("Extracted ID:", student_id)
    # Then show the full processed response
    response = processor.get_student_details(query)
    print("Full Response:", response)
    print("-" * 50)
    return student_id

    

# if __name__ == "__main__":
#     main()