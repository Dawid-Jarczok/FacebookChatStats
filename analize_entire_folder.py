import sys
import os
from facebook_chat_statistics import FacebookChatStatistics
import time

def process_folder(folder_path, pdf=False, txt=False, user=None):
	if 'message_1.json' in os.listdir(folder_path):
		try:
			fcs = FacebookChatStatistics(folder_path + '/message_1.json')
			fcs.run(pdf, txt, user)
		except Exception as e:
			print('Error "{}" processing folder: {}'.format(e, folder_path))
	else:
		print('message_1.json not found in folder:', folder_path)

def main():
	pdf, txt = False, False
	user = None
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
		
	else:
		print('Usage: python3 {} path/to/inbox'.format(sys.argv[0]))
		print('Optional arguments:')
		print('pdf - generate pdf report')
		print('txt - generate txt report')
		print('user "user_name" - generate report for specific user, e.g. "user Jan_Kowalski"')
		sys.exit()

	if not os.path.isdir(path_to_folder):
		print('Invalid folder path')
		sys.exit()

	folders = [f for f in os.listdir(path_to_folder) if os.path.isdir(os.path.join(path_to_folder, f))]

	start_time = time.time()  # Start measuring time

	for folder in folders:
			folder_path = os.path.join(path_to_folder, folder)
			process_folder(folder_path, pdf, txt, user)

	end_time = time.time()  # Stop measuring time
	execution_time = end_time - start_time

	print('\nExecution time: {:.2f} seconds'.format(execution_time))

if __name__ == '__main__':
	main()
