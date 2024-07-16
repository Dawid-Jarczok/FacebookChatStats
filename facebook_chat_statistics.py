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

warnings.filterwarnings('ignore', module='matplotlib')

class FacebookChatStatistics(FacebookMessengerConversation):

    def __init__(self, path_to_conversation):
        super().__init__(path_to_conversation, 10, 40, 10)
        self.max_participants_on_plots = 10
        self.pdf_fonts = ['Arial', 'Segoe UI Emoji']

        self.timeline, self.nbr_times_day, self.nbr_times_weekday, self.nbr_times_hour = self.get_timeline()

        self.top_emojis, self.emojis_all_count = self.get_top_emojis(self.nbr_top_emojis)
        self.top_reactions_emojis, self.emojis_reactions_all_count = self.get_top_reactions_emojis(self.nbr_top_emojis)

    def run(self, pdf=False, txt=False, user=None):
        if len(self.p) == 0:
            print('{} No participants found in the conversation.'.format(self.title))
            return
        if self.nbr_msg < 10:
            print('{} Not enough messages to generate statistics.'.format(self.title))
            return
        if pdf:
            self.generate_pdf()
        if txt:
            self.generate_txt()
        if user != None:
            self.update_user_statistics(user)
        print('{} Succeeded!.'.format(self.title))

    def print_in_terminal(self):
        print(banner('Times'))
        print('Start: {}\nEnd: {}'.format(self.time_start, self.time_end))
        print('Number of days: {}'.format(self.nbr_days))
        print('Number of days active: {} ({:.3} %)'.format(self.nbr_days_active, 100*self.nbr_days_active/self.nbr_days))
        print('Most messages in one day: {}'.format(max(self.nbr_times_day)))

        print(banner('Messages'))
        print('Number of messages: {}'.format(self.nbr_msg))
        for i, p in enumerate(self.nbr_msg_p, 1):
            print('{}. {: <20}: {} ({:.3} %)'.format(i, p, self.nbr_msg_p[p], 100*self.nbr_msg_p[p]/self.nbr_msg))

        print(banner('Words'))
        print('Number of words: {}'.format(self.nbr_words))
        for i, p in enumerate(self.nbr_words_p, 1):
            print('{}. {: <20}: {} ({:.3} %)'.format(i, p, self.nbr_words_p[p], 100*self.nbr_words_p[p]/self.nbr_words))

        print('Top {} words: {}'.format(min(self.nbr_top_words, 10), list(self.top_words.keys())[:10]))
        for i, p in enumerate(self.top_words_p, 1):
            print('{}. {: <20}: {}'.format(i, p, list(self.top_words_p[p].keys())[:10]))
        
        print(banner('Characters'))
        print('Number of characters: {}'.format(self.nbr_chars))
        for i, p in enumerate(self.nbr_chars_p, 1):
            if len(self.p) > 10 and self.nbr_chars_p[p] == 0:
                continue
            print('{}. {: <20}: {} ({:.3} %)'.format(i, p, self.nbr_chars_p[p], 100*self.nbr_chars_p[p]/self.nbr_chars))
        print('Top {} characters: {}'.format(self.nbr_top_characters, list(self.top_chars.keys())[self.nbr_top_characters]))

        print(banner('Averages'))
        print('Average messages per day: {:.1f}'.format(self.avg_msg_per_day))
        print('Average length of messages: {:.1f} words'.format(self.avg_words_per_msg))
        print('Average length of messages: {:.1f} characters'.format(self.avg_chars_per_msg))
        print('Average length of word: {:.1f} characters'.format(self.avg_chars_per_word))
        for i, p in enumerate(self.nbr_words_p, 1):
            if len(self.p) > 10 and self.nbr_words_p[p] == 0:
                continue
            print('{}. {: <20}: {:.1f} w/msg\t{:.1f} ch/msg\t{:.1f} ch/w'.format(i, p, self.avg_words_per_msg_p[p], self.avg_chars_per_msg_p[p], self.avg_chars_per_word_p[p]))

        print(banner('Edits'))
        print('Number of editions: {}'.format(self.nbr_editions))
        for i, p in enumerate(self.nbr_editions_p, 1):
            if len(self.p) > 10 and self.nbr_editions_p[p] == 0:
                continue
            print('{}. {: <20}: {}'.format(i, p, self.nbr_editions_p[p]))

        # Emojis
        print(banner('Emojis'))
        for i, p in enumerate(self.emojis_all_count, 1):
            if len(self.p) > 10 and self.emojis_all_count[p] == 0:
                continue
            print('{}. {: <20}: {}'.format(i, p, self.emojis_all_count[p]))

        print('Top {} emojis: {}'.format(self.nbr_top_emojis, list(self.top_emojis.keys())))

        # Reactions emojis
        print(banner('Reactions emojis'))
        for i, p in enumerate(self.emojis_reactions_all_count, 1):
            if len(self.p) > 10 and self.emojis_reactions_all_count[p] == 0:
                continue
            print('{}. {: <20}: {}'.format(i, p, self.emojis_reactions_all_count[p]))

        print('Top {} reactions emojis: {}'.format(self.nbr_top_emojis, list(self.top_reactions_emojis.keys())))

    def generate_pdf(self, print_in_terminal=False):
        pb = ProgressBar(13, prefix = self.title, suffix = 'Complete', length = 50)
        if not print_in_terminal: pb.off()

        # Set appropriate filename
        names = ''
        if len(self.p) > 2:
            names = 'Group chat: ' + self.title
        else:
            for p in self.p:
                names += p + ', '
            names = names[:-1]
        filename = self.title + '.pdf'

        # Creating the results directory if it doesn't exist
        if not os.path.exists('results'):
            os.makedirs('results')

        with PdfPages(os.path.join('results', filename)) as pdf:
            #participants_on_plots = participants[:max_participants_on_plots] + (['Rest'] if len(participants) > max_participants_on_plots else [])

            # Plot participants messages percentage
            # Set a wider range of colors for the color cycle
            colors = plt.cm.tab20(np.linspace(0, 1, 20))
            plt.gca().set_prop_cycle('color', colors)
            top_participants_in_messages = self.top_participants_in_messages(self.max_participants_on_plots)
            plt.pie(top_participants_in_messages.values(), startangle=90, autopct='%1.1f%%')
            plt.legend(list(top_participants_in_messages.keys()),
                loc='upper left',
                bbox_to_anchor=(-0.15, 1.15))
            plt.axis('equal')
            plt.title('Messages')
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot participants words percentage
            # Set a wider range of colors for the color cycle
            colors = plt.cm.tab20(np.linspace(0, 1, 20))
            plt.gca().set_prop_cycle('color', colors)
            top_participants_in_words = self.top_participants_in_words(self.max_participants_on_plots)
            plt.pie(list(top_participants_in_words.values()), startangle=90, autopct='%1.1f%%')
            plt.legend(list(top_participants_in_words.keys()),
                    loc='upper left',
                    bbox_to_anchor=(-0.15, 1.15))
            plt.axis('equal')
            plt.title('Words')
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot participants characters percentage
            # Set a wider range of colors for the color cycle
            colors = plt.cm.tab20(np.linspace(0, 1, 20))
            plt.gca().set_prop_cycle('color', colors)
            top_participants_in_characters = self.top_participants_in_characters(self.max_participants_on_plots)
            plt.pie(list(top_participants_in_characters.values()), startangle=90, autopct='%1.1f%%')
            plt.legend(list(top_participants_in_characters.keys()),
                    loc='upper left',
                    bbox_to_anchor=(-0.15, 1.15))
            plt.axis('equal')
            plt.title('Characters')
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Older versions of the chat do not have editions
            if self.nbr_editions > 0:
                # Plot participants editions percentage
                colors = plt.cm.tab20(np.linspace(0, 1, 20))
                plt.gca().set_prop_cycle('color', colors)
                top_participants_in_editions = self.top_participants_in_editions(self.max_participants_on_plots)
                plt.pie(list(top_participants_in_editions.values()), startangle=90, autopct='%1.1f%%')
                plt.legend(list(top_participants_in_editions.keys()),
                        loc='upper left',
                        bbox_to_anchor=(-0.15, 1.15))
                plt.axis('equal')
                plt.title('Messages editions')
                pdf.savefig()
                plt.close()

            pb.printProgressBar()

            # Plot timeline
            months = self.nbr_days/30
            interval = int(round(months/12))
            fmt = mdates.DateFormatter('%Y-%m-%d')
            loc = mdates.MonthLocator(interval=interval)
            ax = plt.axes()
            ax.xaxis.set_major_formatter(fmt)
            plt.bar(self.timeline, self.nbr_times_day, align='center')
            plt.title('Timeline')
            plt.ylabel('Number of messages')
            ax.yaxis.grid(linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_linewidth(0.5)
            ax.spines['left'].set_linewidth(0.5)
            fig = plt.figure(1)
            fig.autofmt_xdate()
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot by hour
            hour = list(range(24))
            plt.bar(hour, self.nbr_times_hour, align='center', width=0.8)
            plt.title('Activity by Hour')
            plt.xlabel('Hour of the day')
            plt.ylabel('Number of messages')
            plt.grid(True)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot by weekday
            weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                            'Friday', 'Saturday', 'Sunday']
            weekday_arr = np.arange(len(weekday_labels))
            plt.bar(weekday_arr, self.nbr_times_weekday, align='center', width=0.8)
            plt.xticks(weekday_arr, weekday_labels, rotation=30)
            plt.title('Activity by Weekday')
            plt.ylabel('Number of messages')
            plt.grid(True)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot top emojis
            plt.rcParams['font.family'] = self.pdf_fonts
            plt.gca().set_prop_cycle('color', colors)

            x = np.arange(len(self.top_emojis))
            if len(self.p) <= self.max_participants_on_plots:
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
        
                for i, participant in enumerate(self.p):
                    # Calculate the x values for the current participant
                    x_offset = i * bar_width - (0.4 - bar_width / 2)
                    plt.bar(x + x_offset, [self.top_emojis[emoji_key][participant] for emoji_key in self.top_emojis], align='center', width=bar_width, label=participant)
                plt.legend(list(self.top_emojis.keys()),
                        loc='upper right',
                        bbox_to_anchor=(1.15, 1.15))
            else:
                plt.bar(x, [self.top_emojis[emoji_key]['all'] for emoji_key in self.top_emojis], align='center')

            plt.xticks(x, self.top_emojis.keys())
            plt.title('Top {} emojis'.format(self.nbr_top_emojis))
            plt.ylabel('Number of times used')
            ax = plt.gca()  # Get the current Axes instance
            ax.yaxis.grid(linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_linewidth(0.5)
            ax.spines['left'].set_linewidth(0.5)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot top reactions emojis
            plt.rcParams['font.family'] = self.pdf_fonts
            plt.gca().set_prop_cycle('color', colors)

            x = np.arange(len(self.top_reactions_emojis))
            if len(self.p) <= self.max_participants_on_plots:
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
        
                for i, participant in enumerate(self.p):
                    # Calculate the x values for the current participant
                    x_offset = i * bar_width - (0.4 - bar_width / 2)
                    plt.bar(x + x_offset, [self.top_reactions_emojis[emoji_key][participant] for emoji_key in self.top_reactions_emojis], align='center', width=bar_width, label=participant)
                plt.legend(list(self.top_reactions_emojis.keys()),
                        loc='upper right',
                        bbox_to_anchor=(1.15, 1.15))
            else:
                plt.bar(x, [self.top_reactions_emojis[emoji_key]['all'] for emoji_key in self.top_reactions_emojis], align='center')
                

            plt.xticks(x, self.top_reactions_emojis)
            plt.title('Top {} reactions emojis'.format(self.nbr_top_emojis))
            plt.ylabel('Number of times used')
            ax = plt.gca()  # Get the current Axes instance
            ax.yaxis.grid(linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_linewidth(0.5)
            ax.spines['left'].set_linewidth(0.5)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot top characters percentage
            # Set a wider range of colors for the color cycle
            colors = plt.cm.tab20(np.linspace(0, 1, 20))
            plt.gca().set_prop_cycle('color', colors)
            fracs = list(self.top_chars.values())[:self.nbr_top_characters]
            # Add the percentage of the rest of the characters
            fracs.append(self.nbr_chars - sum(fracs))
            plt.pie(fracs, startangle=90, autopct='%1.1f%%')
            plt.legend(list(self.top_chars.keys()) + ['Rest'],
                    loc='upper left',
                    bbox_to_anchor=(-0.15, 1.15))
            plt.axis('equal')
            plt.title('Top {} characters'.format(self.nbr_top_characters))
            pdf.savefig()
            plt.close()
            pb.printProgressBar()
            

            # Text statistics
            plt.rcParams['font.family'] = self.pdf_fonts
            plt.figure(figsize=(8.27, 11.69))
            plt.title('Text Statistics', fontsize=16, fontweight='bold')
            plt.axis('off')

            text_stats = [
                'Start: {}'.format(self.time_start_str),
                'End: {}'.format(self.time_end_str),
                'Number of days: {}'.format(self.nbr_days),
                'Number of days active: {} ({:.3} %)'.format(self.nbr_days_active, 100*self.nbr_days_active/self.nbr_days),
                'Most messages in one day: {}'.format(max(self.nbr_times_day)),
                'Number of messages: {}'.format(self.nbr_msg),
                'Number of words: {}'.format(self.nbr_words),
                'Number of characters: {}'.format(self.nbr_chars),
                'Top {} characters: {}'.format(self.nbr_top_characters, list(self.top_chars.keys())[self.nbr_top_characters]),
                'Average length of messages: {:.1f} words'.format(self.avg_words_per_msg),
                'Average length of messages: {:.1f} characters'.format(self.avg_chars_per_msg),
                'Average length of word: {:.1f} characters'.format(self.avg_chars_per_word),
                'Average messages per day: {:.1f}'.format(self.avg_msg_per_day),
                'Number of editions: {}'.format(self.nbr_editions),
            ]

            y = 1.0
            for elem in text_stats:
                plt.text(0.0, y, elem, fontsize=12, verticalalignment='center')
                y -= 0.025

            s = ""
            for i, p in enumerate(list(self.nbr_msg_p.keys())[:self.max_participants_on_plots], 1):
                s += '{}. {: <25}: {:2.1f} w/msg   {:2.1f} ch/msg   {:2.1f} ch/w'.format(i, p, self.avg_words_per_msg_p[p], self.avg_chars_per_msg_p[p], self.avg_chars_per_word_p[p]) + '\n'
                y -= 0.012
            plt.text(0.0, y, s, fontsize=12, verticalalignment='center')

            # Emojis
            s = f'Top {self.nbr_top_emojis} emojis: {list(self.top_emojis.keys())}\n'
            for i, p in enumerate(self.emojis_all_count, 1):
                if i > self.max_participants_on_plots:
                    break
                if self.emojis_all_count[p] == 0:
                    continue
                s += f'{i}. {p}: {self.emojis_all_count[p]}' + '\n'
            # Reactions emojis
            s += f'Top {self.nbr_top_emojis} reactions emojis: {list(self.top_reactions_emojis.keys())}\n'
            for i, p in enumerate(self.emojis_reactions_all_count, 1):
                if i > self.max_participants_on_plots:
                    break
                if self.emojis_reactions_all_count[p] == 0:
                    continue
                s += f'{i}. {p}: {self.emojis_reactions_all_count[p]}' + '\n'
            plt.text(0.0, 0.16, s, fontsize=12, verticalalignment='center')

            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Top words
            plt.rcParams['font.family'] = self.pdf_fonts
            plt.figure(figsize=(8.27, 11.69))
            plt.title('Top words', fontsize=16, fontweight='bold')
            plt.axis('off')

            y = 0.95
            x = 0.0
            for j, word in enumerate(list(self.top_words.keys())[:self.nbr_top_words]):
                    plt.text(x, y - 0.025*(j+1), '{}. {}: {}'.format(j+1, list(self.top_words.keys())[j], list(self.top_words.values())[j]), fontsize=12, verticalalignment='center')
            for i, p in enumerate(self.p, 1):
                y = 0.95
                plt.text(x + 0.22*i, y, p.split()[0], fontsize=12, verticalalignment='center')
                for j, word in enumerate(list(self.top_words_p[p].keys())[:self.nbr_top_words], 1):
                    plt.text(x + 0.22*i, y - 0.025*j, '{}: {}'.format(word, self.top_words_p[p][word]), fontsize=12, verticalalignment='center')

            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # PDF info
            d = pdf.infodict()
            d['Title'] = filename
            d['Author'] = 'Facebook Chat Statistics'
            d['Subject'] = 'Conversation: {}'.format(names)
            d['CreationDate'] = datetime.today()
            d['ModDate'] = datetime.today()

        pb.printProgressBar()
        if print_in_terminal: print('\nPDF \'{}\' generated successfully!'.format(filename))
    
    def generate_txt(self, print_in_terminal=False):
        # Create a text file for better readability of statistics especialy for large groups chats
        txt_filename = self.title + '.txt'
        txt_file_path = os.path.join('results', txt_filename)
        with open(txt_file_path, 'w', encoding='utf8') as txt:
            txt.write(banner('Times') + '\n')
            txt.write('Start: {}\nEnd: {}\n'.format(self.time_start_str, self.time_end_str))
            txt.write('Number of days: {}\n'.format(self.nbr_days))
            txt.write('Number of days active: {} ({:.3} %)\n'.format(self.nbr_days_active, 100*self.nbr_days_active/self.nbr_days))
            txt.write('Most messages in one day: {}\n'.format(max(self.nbr_times_day)))

            txt.write(banner('Messages') + '\n')
            txt.write('Number of messages: {}\n'.format(self.nbr_msg))
            for i, p in enumerate(self.nbr_msg_p, 1):
                txt.write('{: >3}. {: <25}: {} ({:.3} %)\n'.format(i, p, self.nbr_msg_p[p], 100*self.nbr_msg_p[p]/self.nbr_msg))

            txt.write(banner('Words') + '\n')
            txt.write('Number of words: {}\n'.format(self.nbr_words))
            for i, p in enumerate(self.nbr_words_p, 1):
                txt.write('{: >3}. {: <25}: {} ({:.3} %)\n'.format(i, p, self.nbr_words_p[p], 100*self.nbr_words_p[p]/self.nbr_words))
            
            txt.write(banner('Characters') + '\n')
            txt.write('Number of characters: {}\n'.format(self.nbr_chars))
            txt.write('Top {} characters: {}\n'.format(self.nbr_top_characters, list(self.top_chars.keys())[:self.nbr_top_characters]))
            for i, p in enumerate(self.nbr_chars_p, 1):
                txt.write('{: >3}. {: <25}: {} ({:.3} %)\n'.format(i, p, self.nbr_chars_p[p], 100*self.nbr_chars_p[p]/self.nbr_chars))

            txt.write(banner('Averages') + '\n')
            txt.write('Average messages per day: {:.1f}\n'.format(self.avg_msg_per_day))
            txt.write('Average length of messages: {:.1f} words\n'.format(self.avg_words_per_msg))
            txt.write('Average length of messages: {:.1f} characters\n'.format(self.avg_chars_per_msg))
            txt.write('Average length of word: {:.1f} characters\n'.format(self.avg_chars_per_word))
            for i, p in enumerate(self.nbr_words_p, 1):
                txt.write('{: >3}. {: <25}: {:.1f} w/msg\t{:.1f} ch/msg\t{:.1f} ch/w\n'.format(i, p, self.avg_words_per_msg_p[p], self.avg_chars_per_msg_p[p], self.avg_chars_per_word_p[p]))

            txt.write(banner('Edits') + '\n')
            txt.write('Number of editions: {}\n'.format(self.nbr_editions))
            for i, p in enumerate(self.nbr_editions_p, 1):
                txt.write('{: >3}. {: <25}: {}\n'.format(i, p, self.nbr_editions_p[p]))

            # Emojis
            txt.write(banner('Emojis') + '\n')
            txt.write('Top {} emojis: {}\n'.format(self.nbr_top_emojis, list(self.top_emojis.keys())))
            for i, p in enumerate(self.emojis_all_count, 1):
                txt.write('{: >3}. {: <25}: {}\n'.format(i, p, self.emojis_all_count[p]))

            # Reactions emojis
            txt.write(banner('Reactions emojis') + '\n')
            txt.write('Top {} reactions emojis: {}\n'.format(self.nbr_top_emojis, list(self.top_reactions_emojis.keys())))
            for i, p in enumerate(self.emojis_reactions_all_count, 1):
                txt.write('{: >3}. {: <25}: {}\n'.format(i, p, self.emojis_reactions_all_count[p]))

            txt.write(banner('Top words') + '\n')
            if len(self.p) <= 10:
                column_width = 25
                for i in range(0, len(self.p) + 1):
                    if i == 0:
                        txt.write('Top words'.ljust(column_width))
                    else:
                        txt.write((str(i) + '. ' + self.p[i-1]).ljust(column_width))
                txt.write('\n')
                for i in range(len(list(self.top_words.keys())[:self.nbr_top_words])):
                    txt.write('{}. {} ({})'.format(i + 1, list(self.top_words.keys())[i], list(self.top_words.values())[i]).ljust(column_width))
                    for j, p in enumerate(self.top_words_p, 1):
                        if i < len(list(self.top_words_p[p].keys())):
                            txt.write('{} ({})'.format(list(self.top_words_p[p].keys())[i], list(self.top_words_p[p].values())[i]).ljust(column_width))
                        else:
                            txt.write(' '.ljust(column_width))
                    txt.write('\n')
            else:
                #Writing with tabulation for importing to excel
                for i in range(0, len(self.p) + 1):
                    if i == 0:
                        txt.write('Top words\t')
                    else:
                        txt.write((str(i) + '. ' + self.p[i-1]) + '\t')
                txt.write('\n')
                for i in range(len(list(self.top_words.keys())[:self.nbr_top_words])):
                    txt.write('{}. {} ({})'.format(i + 1, list(self.top_words.keys())[i], list(self.top_words.values())[i]) + '\t')
                    for j, p in enumerate(self.top_words_p, 1):
                        if i < len(list(self.top_words_p[p].keys())):
                            txt.write('{} ({})'.format(list(self.top_words_p[p].keys())[i], list(self.top_words_p[p].values())[i]) + '\t')
                        else:
                            txt.write(' \t')
                    txt.write('\n')

        if print_in_terminal: print('\ntxt \'{}\' generated successfully!'.format(txt_filename))

    def update_user_statistics(self, user):
        user_statistics_path = os.path.join('results', 'user_statistics.json')

        top_emojis_with_count = {key : self.top_emojis[key]['all'] for key in self.top_emojis}
        top_emojis_reactions_with_count = {key : self.top_reactions_emojis[key]['all'] for key in self.top_reactions_emojis}

        user_statistics = {
            'conversation_type': 'group' if len(self.p) > 2 else 'private',
            'times': {'start': self.time_start_str,
                'end': self.time_end_str,
                'days': self.nbr_days,
                'active_days': self.nbr_days_active,
                'most_messages_in_one_day': max(self.nbr_times_day)},
            'messages': {'all': self.nbr_msg,
                'user': self.nbr_msg_p[user]},
            'words': {'all': self.nbr_words,
                'user': self.nbr_words_p[user],
                'top': dict(list(self.top_words.items())[:self.nbr_top_words]),
                'user_top': dict(list(self.top_words_p[user].items())[:self.nbr_top_words])},
            'characters': {'all': self.nbr_chars,
                'user': self.nbr_chars_p[user],
                'top': dict(list(self.top_chars.items())[:self.nbr_top_characters])},
            'averages': {'messages_per_day': round(self.avg_msg_per_day, 1),
                'words_per_message': round(self.avg_words_per_msg, 1),
                'characters_per_message': round(self.avg_chars_per_msg, 1),
                'characters_per_word': round(self.avg_chars_per_word, 1)},
            'edits': {'all': self.nbr_editions,
                'user': self.nbr_editions_p[user]},
            'emojis': {'all': sum(self.emojis_all_count.values()),
                'user': self.emojis_all_count[user],
                'top': top_emojis_with_count},
            'reactions_emojis': {'all': sum(self.emojis_reactions_all_count.values()),
                    'user': self.emojis_reactions_all_count[user],
                    'top': top_emojis_reactions_with_count},
        }
        if not os.path.isfile(user_statistics_path):
            with open(user_statistics_path, 'w') as json_file:
                json.dump({'conversations': {}}, json_file, indent=2)
        
        data = json.load(open(user_statistics_path))
        data['conversations'].update({self.title: user_statistics})
        with open(user_statistics_path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

def main():
    """
    Fetches and prints statistics of a Facebook Messenger
    conversation. Also generates a PDF with plots of
    some of these statistics.
    """
    user = None

    if len(sys.argv) == 2:
        path_to_conversation = str(sys.argv[1])
    elif len(sys.argv) == 3:
        path_to_conversation = str(sys.argv[1])
        user = str(sys.argv[2]).replace('_', ' ')
    else:
        print('Usage: python3 {} chats/Conversation.json [Opional: user_name for user statistics]'
        .format(sys.argv[0]))
        sys.exit()

    fb = FacebookChatStatistics(path_to_conversation)

    if len(fb.p) == 0:
        print('{} No participants found in the conversation.'.format(fb.title))
        sys.exit()
    
    fb.print_in_terminal()
    
    if fb.nbr_msg < 10:
        print(fb.title, ' Not enough messages to generate statistics.')
        sys.exit()
    
    fb.generate_pdf(True)
    fb.generate_txt(True)
    if user != None:
        fb.update_user_statistics(user)

    
def banner(msg, ch='=', length=80):
    """Creates a banner with the message `msg`.

    Args:
        msg (str): Message of banner.
        ch (str): Banner character.
        length (int): Length of banner.

    Returns:
        str: Banner with message.

    """
    spaced_text = ' {} '.format(msg)
    banner = spaced_text.center(length, ch)
    return banner

if __name__ == '__main__':
    main()
