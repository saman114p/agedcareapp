import os
import requests
import sqlite3
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
endpoint = os.getenv("ENDPOINT_URL")
api_key = os.getenv("API_KEY")
deployment = os.getenv("DEPLOYMENT_NAME")
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_key = os.getenv("SEARCH_KEY")
search_index = os.getenv("SEARCH_INDEX_NAME")

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
    try:
        response = requests.post(search_url, headers=headers, json=data)
        response.raise_for_status()
        search_results = response.json()
        return search_results
    except requests.exceptions.RequestException as e:
        print(f"Search request error: {e}")
        if e.response is not None:
            print(f"Search response content: {e.response.content}")
        return {}

# Function to make a request to Azure OpenAI with search results as context
def get_openai_completion(query, context):
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-05-01-preview"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant that helps users to find relevant information about Patients that are also referred as Customers with Unique ID (Customer ID) using Clinical Notes."
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
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        if e.response is not None:
            print(f"Response content: {e.response.content}")
        return {}

# Function to format the output
def format_output(result):
    if 'choices' in result:
        content = result['choices'][0]['message']['content']
        # Replace asterisks and hash symbols
        formatted_content = content.replace('*', '').replace('#', '').strip()
        return formatted_content
    else:
        return "No valid response received from the OpenAI API."

@app.route('/')
def index():
    if 'username' in session:
        username = session.get('username')
        role = session.get('role')
        return render_template('index.html', username=username, role=role)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['username'] = user[1]
            session['role'] = user[3]
            flash(f'Logged in successfully as {username} with role of {user[3]}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return redirect(url_for('login'))
    query = request.form['question']
    search_results = search_documents(query)

    # Extract context from search results
    if 'value' in search_results:
        context = "\n".join([doc['content'] for doc in search_results['value'] if 'content' in doc])
    else:
        context = "No relevant information found."

    # Get the completion result
    result = get_openai_completion(query, context)

    # Format the output
    formatted_output = format_output(result)
    
    return jsonify({'answer': formatted_output})

if __name__ == '__main__':
    app.run(debug=True)
