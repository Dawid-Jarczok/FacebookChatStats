import os
import sys
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import warnings
from facebook_messenger_conversation import FacebookMessengerConversation
from progress_bar import ProgressBar
import json
import time

def main():
    path = str(sys.argv[1])
    if not os.path.isfile(path):
        print('No file in path')
        return
    data = json.load(open(path))
    print('User: ', data['user'])
    conv_data = {
        'time_start': {},
        'days': {},
        'active_days': {},
        'active_days_in_row': {},
        'most_messages_in_one_day': {},
        'messages_all': {},
        'messages_user': {},
        'messages_per_day': {},
        'words_per_message': {},
        'photos_all': {},
        'photos_user': {},
        'videos_all': {},
        'videos_user': {},
        'audio_all': {},
        'audio_user': {},
        'msg_per_emoji': {},
        'msg_per_emoji_user': {},
        'msg_per_reaction': {},
        'msg_per_reaction_user': {},
    }

    all_nbr = {
        'messages_all': 0,
        'messages_user': 0,
        'words_all': 0,
        'words_user': 0,
        'edits_user': 0,
        'photos_all': 0,
        'photos_user': 0,
        'videos_all': 0,
        'videos_user': 0,
        'audio_all': 0,
        'audio_user': 0,
    }

    for title in data['conversations']:
        conversation = data['conversations'][title]
        for key in all_nbr.keys():
            if key in conversation.keys():
                all_nbr[key] += conversation[key]
    
    all_nbr_averages = {
        'words_per_message_all': all_nbr['words_all'] / all_nbr['messages_all'],
        'words_per_message_user': all_nbr['words_user'] / all_nbr['messages_user'],
    }
    all_nbr.update(all_nbr_averages)

    for title in data['conversations']:
        conversation = data['conversations'][title]
        
        for key in conv_data.keys():
            if key not in conversation.keys():
                print(f"ERROR - no {key} in user_statistics")
                continue
            if key in ['msg_per_emoji', 'msg_per_reaction', 'msg_per_emoji_user', 'msg_per_reaction_user'] and conversation[key] == 0:
                continue
            conv_data[key].update({title: conversation[key]})
        

    for key, elem in conv_data.items():
        reverse = True
        if key in ['msg_per_emoji', 'msg_per_reaction', 'msg_per_emoji_user', 'msg_per_reaction_user']: reverse = False
        conv_data[key] = dict(sorted(elem.items(), key=lambda item: item[1], reverse=reverse))

    nbr_of_max_conversations = 10

    print(f'* time_start')
    n = nbr_of_max_conversations // 2
    l = [i for i, e in enumerate(conv_data['time_start'].values())]
    l = set(l[:n] + l[-n:])
    for i, (t, e) in enumerate(conv_data['time_start'].items()):
        if i not in l: continue
        print_dict_item(i, t, e)

    for key, elem in conv_data.items():
        if key == 'time_start': continue
        print(f'* {key}')
        for i, (t, e) in enumerate(list(elem.items())[:nbr_of_max_conversations]):
            if e == 0: continue
            elems4percentage = {'messages_user': 'messages_all', 'photos_user': 'photos_all', 'videos_user': 'videos_all', 'audio_user': 'audio_all'}
            if key in elems4percentage.keys():
                print_dict_item(i, t, e, conv_data[elems4percentage[key]][t])
            else:
                print_dict_item(i, t, e)
    
    print('')
    print('---- SUM ----')
    for key, elem in all_nbr.items():
        if type(elem) == float:
            print(f'{key}: {elem:.2f}')
        else:
            print(f'{key}: {elem}')

def print_dict_item(i, key, elem, all=0):
    if type(elem) == float:
        if all == 0:
            print(f'{i+1:>4}. {elem:<5.2f}   {key}')
        else:
            p = elem / all * 100
            print(f'{i+1:>4}. {elem:<5.2f} ({p:.1f}%)   {key}')
    else:
        if all == 0:
            print(f'{i+1:>4}. {elem:<5}   {key}')
        else:
            p = elem / all * 100
            print(f'{i+1:>4}. {elem:<5} ({p:.1f}%)   {key}')

if __name__ == '__main__':
    main()