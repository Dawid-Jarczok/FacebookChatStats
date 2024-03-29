import json
import os

def combine_messages(output_dir):
    # Get the path to the current directory
    current_dir = os.getcwd()
    raw_chats_dir = os.path.join(current_dir, 'raw-chats')

    if not os.path.exists(raw_chats_dir) or not os.path.isdir(raw_chats_dir):
        print("The 'raw-chats' directory does not exist.")
        return

    # Find all message_x.json files in the raw-chats directory
    message_files = [f for f in os.listdir(raw_chats_dir) if f.startswith('message_') and f.endswith('.json')]

    if not message_files:
        print("No message files found in the 'raw-chats' directory.")
        return

    # Sort the files numerically based on the number after the underscore
    message_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))

    # Initialize an empty list to store combined messages
    combined_messages = []

    # Iterate over the message files and combine their messages
    for filename in message_files:
        file_path = os.path.join(raw_chats_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Append the messages from the current file to the combined messages list
            combined_messages.extend(data.get('messages', []))

    # Load message_1.json as base file
    base_file_path = os.path.join(raw_chats_dir, 'message_1.json')
    with open(base_file_path, 'r', encoding='utf-8') as base_file:
        base_data = json.load(base_file)

    # Merge combined messages with the data from message_1.json
    base_data['messages'] = combined_messages

    # Write combined data to the output directory
    output_file = os.path.join(output_dir, 'message_1.json')
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(base_data, file, ensure_ascii=True, indent=2)

    # Print confirmation message
    print("Combined JSON Data successfully written to message_1.json")

# Combine messages into message_1.json and save to ./chats directory
combine_messages(os.path.join('.', 'chats'))
