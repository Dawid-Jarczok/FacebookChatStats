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
        'most_messages_in_one_day': {},
        'messages_all': {},
        'messages_user': {},
        'messages_per_day': {},
        'words_per_message': {},
        'photos_all': {},
        'photos_user': {},
    }


    for title in data['conversations']:
        conversation = data['conversations'][title]
        
        for key in conv_data.keys():
            if key not in conversation.keys():
                print(f"ERROR - no {key} in user_statistics")
            conv_data[key].update({title: conversation[key]})
        

    for key, elem in conv_data.items():
        conv_data[key] = dict(sorted(elem.items(), key=lambda item: item[1], reverse=True))

    nbr_of_max_conversations = 10

    print(f'* time_start')
    n = nbr_of_max_conversations // 2
    l = [i for i, e in enumerate(conv_data['time_start'].values())]
    l = set(l[:n] + l[-n:])
    for i, (t, e) in enumerate(conv_data['time_start'].items()):
        if i not in l: continue
        print(f'{i+1:>4}. {e}   {t}')

    for key, elem in conv_data.items():
        if key == 'time_start': continue
        print(f'* {key}')
        for i, (t, e) in enumerate(list(elem.items())[:nbr_of_max_conversations]):
            print(f'{i+1:>4}. {e:<6} {t}')

if __name__ == '__main__':
    main()