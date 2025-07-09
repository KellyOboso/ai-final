import os
import logging
import yaml
import spacy

# Download the spaCy English model if not already installed
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    
logging.basicConfig(level=logging.INFO)

DATABASE_FILE = "db.sqlite3"
DATA_DIRECTORY = 'data'

def train_chatbot():
    if os.path.exists(DATABASE_FILE):
        try:
            os.remove(DATABASE_FILE)
            print("Old database removed. Training new database.")
        except OSError as e:
            print(f"Error removing old database {DATABASE_FILE}: {e}")
            print("Please ensure the database file is not in use and try again.")
            return
    else:
        print("No database found. Creating a new database during training.")

    from chatterbot import ChatBot
    from chatterbot.trainers import ListTrainer

    english_bot = ChatBot(
        'MentalHealthBot',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri=f'sqlite:///{DATABASE_FILE}',
        logic_adapters=[
            'chatterbot.logic.BestMatch'
        ],
        read_only=False
    )

    trainer = ListTrainer(english_bot)

    if not os.path.exists(DATA_DIRECTORY):
        print(f"Error: Training data directory '{DATA_DIRECTORY}' not found.")
        print("Please create a 'data' folder and place your conversation files inside.")
        return

    training_files = os.listdir(DATA_DIRECTORY)
    if not training_files:
        print(f"No training files found in '{DATA_DIRECTORY}'. Bot will have no knowledge.")
        return

    for file_name in training_files:
        file_path = os.path.join(DATA_DIRECTORY, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.yml'):
            print(f'Training using {file_name}...')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)

                flattened_conversation = []
                if isinstance(yaml_data, list):
                    for pair in yaml_data:
                        if isinstance(pair, list) and len(pair) == 2:
                            flattened_conversation.extend(pair)
                        elif isinstance(pair, str):
                            continue
                        else:
                            logging.warning(f"Skipping malformed entry in {file_name}: {pair}")
                else:
                    logging.warning(f"Skipping non-list YAML content in {file_name}. Expected a list.")

                if flattened_conversation:
                    trainer.train(flattened_conversation)
                    print(f"Training completed for {file_name}.")
                else:
                    print(f"No conversational data found in {file_name}. Skipping training for this file.")

            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {file_name}: {e}")
            except Exception as e:
                print(f"Error training with {file_name}: {e}")
        else:
            print(f"Skipping non-YAML or non-file entry: {file_name}")

    print("\nChatbot training process finished.")

if __name__ == "__main__":
    train_chatbot()
