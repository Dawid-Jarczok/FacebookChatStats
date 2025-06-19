import os
import sys
import shutil
import json
import time
from progress_bar import ProgressBar

def join_data(data_1, data_2):
        """ Joins two conversations together
            Args:
                data_1 (dict): First conversation data
                data_2 (dict): Second conversation data

            Returns:
                dict: Combined conversation
        """
        new_data = data_1
        new_data['participants'].extend(data_2['participants'])
        new_data['messages'].extend(data_2['messages'])
        new_data['magic_words'].extend(data_2['magic_words'])
        return new_data


def join_json_files(list_of_json_files):
    data = json.load(open(list_of_json_files[0]))

    for path_to_json in list_of_json_files[1:]:
        new_data = json.load(open(path_to_json))
        data = join_data(data, new_data)
    return data
    

def copy_folder(src, dst):
    if not os.path.exists(src):
        return
    
    if not os.path.exists(dst):
        os.makedirs(dst)

    # Iterate through all conversations
    listdir = os.listdir(src)
    pb = ProgressBar(len(listdir), prefix = 'Progress', suffix = 'Complete', length = 50)
    for conv in listdir:
        src_conv = os.path.join(src, conv)
        dst_conv = os.path.join(dst, conv)
        if not os.path.isdir(src_conv):
            continue  # Skip if it's not a directory
        
        # Copy the conversation if it doesn't exist in the destination
        if not os.path.exists(dst_conv):
            #print(f'New conversation: {conv}')
            shutil.copytree(src_conv, dst_conv)
            continue

        # Iterate through all items in the conversation for copying subfolders
        for item in os.listdir(src_conv):
            src_item_path = os.path.join(src_conv, item)
            dst_item_path = os.path.join(dst_conv, item)

            if os.path.isdir(src_item_path):
                #print(f'Copying folder: {src_item_path} to {dst_item_path}')
                shutil.copytree(src_item_path, dst_item_path, dirs_exist_ok=True)

        src_messages = []
        dst_messages = []
        for item in os.listdir(src_conv):
            if item.endswith('.json'):
                item_path = os.path.join(src_conv, item)
                src_messages.append(item_path)
        for item in os.listdir(dst_conv):
            if item.endswith('.json'):
                item_path = os.path.join(dst_conv, item)
                dst_messages.append(item_path)

        # Newest messages are in 1st file, on the top
        all_messages = src_messages + dst_messages
        if len(all_messages) == 0:
            pb.printProgressBar()
            continue
        data = join_json_files(all_messages)

        # Remove duplicates from participants
        seen_participants = set()
        unique_participants = []
        for participant in data['participants']:
            participant_name = participant['name']
            if participant_name not in seen_participants:
                seen_participants.add(participant_name)
                unique_participants.append(participant)
        data['participants'] = unique_participants

        # Remove duplicates from messages
        seen = set()
        unique_messages = []

        for msg in data['messages']:
            timestamp = msg['timestamp_ms']
            if timestamp not in seen:
                seen.add(timestamp)
                unique_messages.append(msg)

            # idx = str(msg['timestamp_ms']) + str(msg['sender_name'])
            # if idx not in seen:
            #     seen.add(idx)
            #     unique_messages.append(msg)
        data['messages'] = unique_messages

        # Delete files in the destination folder
        for item in os.listdir(dst_conv):
            if item.endswith('.json'):
                item_path = os.path.join(dst_conv, item)
                os.remove(item_path)
    
        # Save the combined data to a new file
        new_file_path = os.path.join(dst_conv, 'message_1.json')
        with open(new_file_path, 'w') as new_file:
            json.dump(data, new_file, indent=2)

        pb.printProgressBar()

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 {} path/to/destination/folder path/to/source/folder'.format(sys.argv[0]))
        sys.exit()
    
    dst = str(sys.argv[1])
    src = str(sys.argv[2])

    if not os.path.isdir(dst):
        print('Invalid destination folder')
        sys.exit()
    
    if not os.path.isdir(src):
        print('Invalid source folder')
        sys.exit()

    copy_folder(src, dst)


if __name__ == '__main__':
    main()