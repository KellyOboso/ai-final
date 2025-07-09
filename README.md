Mental Health Chatbot
This is a simple web-based Mental Health Chatbot built with Flask and ChatterBot. It provides a conversational interface for general mental well-being support, along with a sidebar for helpful tips and resources, and a feature to view past conversation history.

Features
Interactive Chatbot: Responds to user queries using a trained ChatterBot model.

Low Confidence Handling: Provides a default response if the chatbot's confidence in its answer is too low.

"Exit" Command: When a user types "exit", the bot responds with encouraging messages (affirmations).

Conversation History: Saves chat sessions to text files and allows users to view them through a dedicated history page.

Dynamic UI: Includes a loading screen and smooth transitions.

Responsive Design: Adapts to different screen sizes (desktop and mobile).

Glassy Theme: Modern, translucent UI elements.

Static Sidebar Content: Displays helpful tips and resources in a persistent sidebar.

User Authentication Placeholders: Includes basic routes for user registration and login (dummy functionality).

Project Structure
.
├── app.py                  # Main Flask application
├── train.py                # Script to train the ChatterBot model
├── data/                   # Directory for chatbot training data (YAML files)
│   ├── conversations.yml   # Example training data
│   └── affirmations.yml    # Affirmations for 'exit' command
├── templates/              # HTML templates for Flask
│   ├── index.html          # Main chatbot page
│   ├── register.html       # User registration page
│   ├── login.html          # User login page
│   └── history.html        # Page to display conversation history
├── static/                 # Static files (CSS, JS)
│   ├── style.css           # Global CSS styles
│   └── scripts/
│       └── script.js       # JavaScript for chatbot functionality
└── saved_conversations/    # Directory where chat histories are saved (created automatically)

Setup and Installation
Follow these steps to get the Mental Health Chatbot running on your local machine.

Prerequisites
Python 3.x

pip (Python package installer)

1. Clone the Repository (if applicable)
If this project is in a repository, clone it:

git clone <repository_url>
cd <project_directory>

Otherwise, ensure you have all the project files in a single directory.

2. Create a Virtual Environment (Recommended)
It's good practice to use a virtual environment to manage dependencies.

python3 -m venv venv

3. Activate the Virtual Environment
On macOS/Linux:

source venv/bin/activate

On Windows:

.\venv\Scripts\activate

4. Install Dependencies
Install the required Python packages.

pip install Flask chatterbot PyYAML

5. Prepare Training Data
Ensure you have your chatbot training data in the data/ directory. These should be YAML files (e.g., conversations.yml). Also, make sure affirmations.yml is present for the "exit" command.

Example data/affirmations.yml content:

- "You are stronger than you think."
- "Take a deep breath and focus on the present moment."
- "Small steps lead to big changes. Celebrate your progress!"
# ... more affirmations

6. Train the Chatbot
Run the train.py script to train your ChatterBot model. This will create or update the db.sqlite3 database.

python3 train.py

Important: If you make changes to your .yml training data files, you must re-run python3 train train.py to update the chatbot's knowledge. It's often recommended to delete db.sqlite3 before re-training for a clean slate.

7. Run the Flask Application
Start the Flask development server.

python3 app.py

Usage
After running app.py, open your web browser and navigate to http://127.0.0.1:5000/.

You will see the Mental Health Chatbot interface.

Type your messages in the input field at the bottom and press "Send" or Enter.

The sidebar on the left provides helpful tips and resources.

To view past conversations, click the "History" link in the navigation bar.

To clear the current chat session's history from your browser, click "Clear Chat".

To end a conversation and receive encouraging messages, type "exit" in the chat.

Important Notes
Local Storage: The chat history is saved in your browser's local storage. If you clear your browser's data or use a different browser/device, the history will not persist.

Database: The db.sqlite3 file stores the chatbot's trained knowledge. Do not manually edit this file.

Conversation Files: Individual conversation sessions are saved as text files in the saved_conversations/ directory on your server.

Development Mode: The application runs in debug mode (debug=True) which is suitable for development but should be disabled for production environments.

Professional Help Disclaimer: Always remember that this chatbot is for general support and is not a substitute for professional medical advice or therapy.