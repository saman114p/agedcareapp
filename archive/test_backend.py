import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
endpoint = os.getenv("ENDPOINT_URL")
api_key = os.getenv("API_KEY")
deployment = os.getenv("DEPLOYMENT_NAME")
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_key = os.getenv("SEARCH_KEY")
search_index = os.getenv("SEARCH_INDEX_NAME")

# Check if environment variables are loaded correctly
if not all([endpoint, api_key, deployment, search_endpoint, search_key, search_index]):
    print("Error: Not all environment variables are loaded. Please check your .env file.")
    exit(1)

# Print environment variables for debugging
print(f"Using endpoint: {endpoint}")
print(f"Using deployment: {deployment}")
print(f"Using search endpoint: {search_endpoint}")
print(f"Using search index: {search_index}")

# Set up headers for Azure OpenAI with API Key
headers_openai = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

# Set up headers for Azure Cognitive Search with API Key
headers_search = {
    "api-key": search_key,
    "Content-Type": "application/json"
}

# Function to perform Azure Cognitive Search
def search_documents(query):
    search_url = f"{search_endpoint}/indexes/{search_index}/docs/search?api-version=2021-04-30-Preview"
    search_data = {
        "search": query,
        "queryType": "semantic",
        "semanticConfiguration": "default",
        "top": 5
    }
    try:
        response = requests.post(search_url, headers=headers_search, json=search_data)
        response.raise_for_status()
        search_results = response.json()
        return search_results
    except requests.exceptions.RequestException as e:
        print(f"Search request error: {e}")
        if e.response is not None:
            print(f"Search response content: {e.response.content}")
        return {}

# Function to make a request to Azure OpenAI with search results as context
def get_openai_completion_with_context(query, context):
    try:
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-05-01-preview"
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that helps users find information based on the provided context."
                },
                {
                    "role": "user",
                    "content": f"{query}\n\nContext:\n{context}"
                }
            ],
            "max_tokens": 800,
            "temperature": 0,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stop": None,
            "stream": False
        }
        print(f"Request URL: {url}")
        print(f"Request Headers: {headers_openai}")
        print(f"Request Data: {data}")
        
        response = requests.post(url, headers=headers_openai, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.content}")
        return {}

# Test the function with a sample query
sample_query = "Summary of customer ID 40045?"
search_results = search_documents(sample_query)

# Extract context from search results
if 'value' in search_results:
    context = "\n".join([doc['content'] for doc in search_results['value'] if 'content' in doc])
else:
    context = "No relevant information found."

result = get_openai_completion_with_context(sample_query, context)
print(result)
