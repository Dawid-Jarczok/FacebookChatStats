import sys
import os
import facebook_chat_statistics as fcs
import subprocess
import multiprocessing
import time

import concurrent.futures

def process_folder(folder_path):
	if 'message_1.json' in os.listdir(folder_path):
		subprocess.run(['python3', 'facebook_chat_statistics.py', folder_path + '/message_1.json', 'False'])
	else:
		print('message_1.json not found in folder:', folder_path)

def main():
	if len(sys.argv) == 2:
		path_to_folder = str(sys.argv[1])
	else:
		print('Usage: python3 {} path/to/inbox'.format(sys.argv[0]))
		sys.exit()

	if not os.path.isdir(path_to_folder):
		print('Invalid folder path')
		sys.exit()

	folders = [f for f in os.listdir(path_to_folder) if os.path.isdir(os.path.join(path_to_folder, f))]

	max_workers = max(1, multiprocessing.cpu_count() // 4)  # Use quarter of the available CPU threads

	start_time = time.time()  # Start measuring time

	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
		executor.map(process_folder, [os.path.join(path_to_folder, folder) for folder in folders])

	end_time = time.time()  # Stop measuring time
	execution_time = end_time - start_time

	print('\nExecution time: {:.2f} seconds'.format(execution_time))

if __name__ == '__main__':
	main()
