import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
endpoint = os.getenv("ENDPOINT_URL", "https://acc1-dev-openai-ae.openai.azure.com/")
api_key = os.getenv("API_KEY")
deployment = os.getenv("DEPLOYMENT_NAME", "clientnotes")
search_endpoint = os.getenv("SEARCH_ENDPOINT", "https://acc1-dev-srch-ae.search.windows.net")
search_key = os.getenv("SEARCH_KEY", "put_your_Azure_AI_Search_admin_key_here")
search_index = os.getenv("SEARCH_INDEX_NAME", "clientnotes")

# Function to perform Azure Cognitive Search
def search_documents(query):
    search_url = f"{search_endpoint}/indexes/{search_index}/docs/search?api-version=2021-04-30-Preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": search_key
    }
    data = {
        "search": query,
        "queryType": "semantic",
        "semanticConfiguration": "default",
        "top": 5
    }
    response = requests.post(search_url, headers=headers, json=data)
    results = response.json()
    return results

# Function to make a request to Azure OpenAI
def get_openai_completion(query, context):
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-05-01-preview"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps users to find relevant information about Patients that are also referred as Customers with Unique ID (Customer ID) using Clinical Notes"
        },
        {
            "role": "user",
            "content": f"{query}\n\nContext:\n{context}"
        }
    ]
    data = {
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
        "stream": False
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to format the output
def format_output(result):
    if 'choices' in result:
        content = result['choices'][0]['message']['content']
        # Replace asterisks and hash symbols
        formatted_content = content.replace('*', '').replace('#', '').strip()
        return formatted_content
    else:
        return "No valid response received from the OpenAI API."

# Test the function with a sample query
sample_query = "Patients that are diagnosed as shortness of breath"
search_results = search_documents(sample_query)

# Extract context from search results
if 'value' in search_results:
    context = "\n".join([doc['content'] for doc in search_results['value'] if 'content' in doc])
else:
    context = "No relevant information found."

# Get the completion result
result = get_openai_completion(sample_query, context)

# Format and print the output
formatted_output = format_output(result)
print(formatted_output)
