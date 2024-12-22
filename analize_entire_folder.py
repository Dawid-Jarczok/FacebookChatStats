import sys
import os
from facebook_chat_statistics import FacebookChatStatistics
import time
import multiprocessing
import numpy as np
import json

def process_folder(args):
    folder_path, pdf, txt, user, log, using_multiprocessing = args
    if 'message_1.json' in os.listdir(folder_path):
        try:
            fcs = FacebookChatStatistics(folder_path + '/message_1.json', using_multiprocessing)
            return fcs.run(pdf, txt, user, log)
        except Exception as e:
            print('Error "{}" processing folder: {}'.format(e, folder_path))
            return None
    else:
        print('message_1.json not found in folder:', folder_path)
        return None

def main():
    pdf, txt, run_multiprocess, log = False, False, False, False
    user = None
    max_active_processes = 4
    if len(sys.argv) >= 2:
        path_to_folder = str(sys.argv[1])
        if 'pdf' in sys.argv:
            pdf = True
        if 'txt' in sys.argv:
            txt = True
        if 'user' in sys.argv:
            try:
                user = str(sys.argv[sys.argv.index('user') + 1]).replace('_', ' ')
            except IndexError:
                print('User name not provided')
                sys.exit()
        if 'run_multiprocess' in sys.argv:
            run_multiprocess = True
            try:
                max_active_processes = int(sys.argv[sys.argv.index('run_multiprocess') + 1])
                max_active_processes = np.clip(max_active_processes, 1, 20)
                print(f'Number of processes: {max_active_processes}')
            except IndexError:
                print(f'Number of processes not provided - using default value {max_active_processes}')
        if 'log' in sys.argv:
            log = True
    else:
        print('Usage: python3 {} path/to/inbox'.format(sys.argv[0]))
        print('Optional arguments:')
        print('log - print detailed logs to console')
        print('pdf - generate pdf report')
        print('txt - generate txt report')
        print('user "user_name" - generate report for specific user, e.g. "user Jan_Kowalski"')
        print(f'run_multiprocess "number"- run script using multiprocessing with specified number of processes (if not provided, default value is {max_active_processes})')
        sys.exit()

    if not os.path.isdir(path_to_folder):
        print('Invalid folder path')
        sys.exit()

    start_time = time.time()  # Start measuring time

    folders = [os.path.join(path_to_folder, f) for f in os.listdir(path_to_folder) if os.path.isdir(os.path.join(path_to_folder, f))]

    if run_multiprocess:
        user_statistics_lst = []
        # Create a pool with a limit of max_active_processes
        with multiprocessing.Pool(processes=max_active_processes) as pool:
            # Prepare arguments for all tasks
            tasks = [(folder_path, pdf, txt, user, log, True) for folder_path in folders]
            # Map tasks to the process pool
            user_statistics_lst = pool.map(process_folder, tasks)
    
        print(f'\nAnalized {len(user_statistics_lst)} conversations')

        path = os.path.join('results', 'user_statistics.json')
        # Create file if not exists
        if not os.path.isfile(path):
            with open(path, 'w') as json_file:
                json.dump({'user': user, 'conversations': {}}, json_file, indent=2)
        
        data = json.load(open(path))
        for elem in user_statistics_lst:
            if elem is None:
                continue
            if data['user'] != user:
                print('Invalid user')
            else:
                data['conversations'].update({elem[0]: elem[1]})
        # Save data to file
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    else:
        for folder_path in folders:
            process_folder((folder_path, pdf, txt, user, log, False))
        print(f'\nAnalized {len(folders)} conversations')

    end_time = time.time()  # Stop measuring time
    execution_time = end_time - start_time

    print(f'Execution time: {execution_time:.2f} seconds\n')

if __name__ == '__main__':
    main()
