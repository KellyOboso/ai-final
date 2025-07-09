from flask import Flask, render_template, request, redirect, url_for, jsonify
from chatterbot import ChatBot
import os
import logging
import datetime
import yaml
import random

logging.basicConfig(level=logging.INFO)

DATABASE_FILE = "db.sqlite3"
SAVE_DIR = 'saved_conversations'
DATA_DIRECTORY = 'data'

os.makedirs(SAVE_DIR, exist_ok=True)

def get_next_conversation_file_number():
    existing_files = []
    for f in os.listdir(SAVE_DIR):
        if f.isdigit():
            existing_files.append(int(f))
        elif f.startswith('conversation_') and f.endswith('.txt'):
            try:
                num_part = f.replace('conversation_', '').replace('.txt', '')
                if num_part.isdigit():
                    existing_files.append(int(num_part))
            except ValueError:
                continue
    existing_files.sort()

    if existing_files:
        return existing_files[-1] + 1
    else:
        return 1

current_conversation_id = get_next_conversation_file_number()

app = Flask(__name__,
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')

english_bot = None
try:
    english_bot = ChatBot(
        'MentalHealthBot',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri=f'sqlite:///{DATABASE_FILE}',
        logic_adapters=[
            'chatterbot.logic.BestMatch'
        ],
        read_only=True
    )
    logging.info(f"ChatBot '{english_bot.name}' initialized and connected to {DATABASE_FILE}")

    initial_bot_message = "Hi there! I'm your Mental Health Support Bot. I'm here to listen and offer general information and coping strategies. Please remember, I am not a substitute for professional help."
    with open(f'{SAVE_DIR}/{current_conversation_id}', 'w', encoding='utf-8') as file:
        file.write(f"--- Conversation Started: {datetime.datetime.now()} ---\n")
        file.write(f'bot : {initial_bot_message}\n')

except Exception as e:
    logging.error(f"Failed to initialize ChatBot: {e}")

@app.route("/")
def home():
    if english_bot is None:
        return "<h1>Chatbot Initialization Error</h1><p>The chatbot failed to load. Please check the server logs.</p>", 500
    initial_bot_message = "Hi there! I'm your Mental Health Support Bot. I'm here to listen and offer general information and coping strategies. Please remember, I am not a substitute for professional help."
    return render_template("index.html", initial_message=initial_bot_message)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        logging.info(f"Register attempt: Username={username}, Email={email}")
        return redirect(url_for('login', message='Registration successful! Please log in.'))
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    message = request.args.get('message')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logging.info(f"Login attempt: Username={username}")
        if username == "test" and password == "password":
            return redirect(url_for('home', message='Login successful!'))
        else:
            return render_template("login.html", error='Invalid username or password.')
    return render_template("login.html", message=message)

@app.route("/get_affirmations")
def get_affirmations():
    affirmations_file_path = os.path.join(DATA_DIRECTORY, 'affirmations.yml')
    if os.path.exists(affirmations_file_path):
        try:
            with open(affirmations_file_path, 'r', encoding='utf-8') as f:
                affirmations = yaml.safe_load(f)
            return jsonify(affirmations)
        except yaml.YAMLError as e:
            logging.error(f"Error loading affirmations.yml: {e}")
            return jsonify({"error": "Failed to load affirmations"}), 500
    return jsonify({"error": "Affirmations file not found"}), 404

@app.route("/history")
def show_history():
    conversations = []
    # Sort files numerically by their filename (which is the ID)
    sorted_filenames = sorted(os.listdir(SAVE_DIR), key=lambda x: int(''.join(filter(str.isdigit, x))) if any(char.isdigit() for char in x) else float('inf'))

    for filename in sorted_filenames:
        file_path = os.path.join(SAVE_DIR, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    conversations.append({'filename': filename, 'content': content})
            except Exception as e:
                logging.error(f"Error reading conversation file {filename}: {e}")
    return render_template("history.html", conversations=conversations)

@app.route("/delete_conversation", methods=['POST'])
def delete_conversation():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({"success": False, "message": "Filename not provided"}), 400

    # Ensure filename is treated as a string before joining
    file_path = os.path.join(SAVE_DIR, str(filename))
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logging.info(f"Deleted conversation file: {filename}")
            return jsonify({"success": True, "message": f"Conversation {filename} deleted successfully."})
        except OSError as e:
            logging.error(f"Error deleting file {filename}: {e}")
            return jsonify({"success": False, "message": f"Error deleting file: {e}"}), 500
    else:
        logging.warning(f"Attempted to delete non-existent file: {filename}")
        return jsonify({"success": False, "message": "File not found"}), 404


@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg').lower().strip()

    if not user_text:
        return "Please type something."

    if english_bot is None:
        return "Chatbot is not available due to an initialization error."

    if user_text == "exit":
        affirmations_file_path = os.path.join(DATA_DIRECTORY, 'affirmations.yml')
        if os.path.exists(affirmations_file_path):
            try:
                with open(affirmations_file_path, 'r', encoding='utf-8') as f:
                    affirmations = yaml.safe_load(f)
                if affirmations and isinstance(affirmations, list):
                    exit_messages = random.sample(affirmations, min(3, len(affirmations)))
                    bot_response = "Thank you for chatting. Remember these thoughts:\n" + "\n".join([f"- {msg}" for msg in exit_messages])
                else:
                    bot_response = "Thank you for chatting. Remember to take care of yourself."
            except yaml.YAMLError as e:
                logging.error(f"Error loading affirmations.yml for exit message: {e}")
                bot_response = "Thank you for chatting. Remember to take care of yourself."
        else:
            bot_response = "Thank you for chatting. Remember to take care of yourself."
        
        with open(f'{SAVE_DIR}/{current_conversation_id}', 'a', encoding='utf-8') as appendfile:
            appendfile.write(f'user : {user_text}\n')
            appendfile.write(f'bot : {bot_response}\n')
        return bot_response

    try:
        response_obj = english_bot.get_response(user_text)

        LOW_CONFIDENCE_THRESHOLD = 0.15
        DEFAULT_LOW_CONFIDENCE_RESPONSE = "I'm here to listen and offer support, but I may not have enough information to answer that. Could you please rephrase or share more about what's on your mind?"

        if response_obj.confidence < LOW_CONFIDENCE_THRESHOLD:
            bot_response = DEFAULT_LOW_CONFIDENCE_RESPONSE
            logging.info(f"User: {user_text} | Bot (Low Confidence): {bot_response} | Confidence: {response_obj.confidence:.2f}")
        else:
            bot_response = str(response_obj)
            logging.info(f"User: {user_text} | Bot: {bot_response} | Confidence: {response_obj.confidence:.2f}")

        with open(f'{SAVE_DIR}/{current_conversation_id}', 'a', encoding='utf-8') as appendfile:
            appendfile.write(f'user : {user_text}\n')
            appendfile.write(f'bot : {bot_response}\n')

        return bot_response

    except Exception as e:
        logging.error(f"Error getting bot response for '{user_text}': {e}")
        return "I'm sorry, I encountered an internal error. Please try again later."


if __name__ == "__main__":
    app.run(debug=True)
