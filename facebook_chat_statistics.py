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

warnings.filterwarnings('ignore', module='matplotlib')

def main():
    """
    Fetches and prints statistics of a Facebook Messenger
    conversation. Also generates a PDF with plots of
    some of these statistics.
    """
    print_in_terminal = True

    if len(sys.argv) == 2:
        path_to_conversation = str(sys.argv[1])
    elif len(sys.argv) == 3:
        path_to_conversation = str(sys.argv[1])
        print_in_terminal = str(sys.argv[2]) == 'True'
    else:
        print('Usage: python3 {} chats/Conversation.json [Opional: print_in_terminal]'
        .format(sys.argv[0]))
        sys.exit()

    fb = FacebookMessengerConversation(path_to_conversation)
    nbr_of_top_emojis = 10
    nbr_of_top_characters = 10
    nbr_of_top_words = 40
    max_participants_on_plots = 10

    pdf_fonts = ['Arial', 'Segoe UI Emoji']

    participants = fb.get_participants()
    if len(participants) == 0:
        print('{} No participants found in the conversation.'.format(fb.title))
        sys.exit()
    start, end = fb.get_time_interval('str')
    nbr_days = fb.get_nbr_days()
    nbr_days_active = fb.get_nbr_days_active()
    timeline, nbr_times_day, nbr_times_weekday, nbr_times_hour = fb.timeline()
    nbr_messages = fb.get_nbr_msg()
    activity = fb.activity()
    nbr_messages_p = {p: activity[p][0] for p in participants}
    nbr_words = fb.get_nbr_words()
    nbr_words_p = fb.get_nbr_words_p()
    top_words = fb.top_words(nbr_of_top_words)
    top_words_p = fb.top_words_p(nbr_of_top_words)

    nbr_characters_p = fb.get_nbr_characters_p()
    nbr_characters = sum(nbr_characters_p.values())
    top_characters = fb.top_characters(nbr_of_top_characters)

    top_emojis, emoji_count_p, emojis_all_count = fb.top_emojis(nbr_of_top_emojis)
    top_reactions_emojis, emoji_reactions_count_p, emojis_reactions_all_count = fb.top_reactions_emojis(nbr_of_top_emojis)

    if print_in_terminal:
        print(banner('Times'))
        print('Start: {}\nEnd: {}'.format(start, end))
        print('Number of days: {}'.format(nbr_days))
        print('Number of days active: {} ({:.3} %)'.format(nbr_days_active, 100*nbr_days_active/nbr_days))
        print('Most messages in one day: {}'.format(max(nbr_times_day)))

        print(banner('Messages'))
        print('Number of messages: {}'.format(nbr_messages))
        for i, (act_p, data) in enumerate(activity.items(), 1):
            print('{}. {: <20}: {} ({:.3} %)'.format(i, act_p, data[0], data[1]))

        print(banner('Words'))
        print('Number of words: {}'.format(nbr_words))
        for i, p in enumerate(nbr_words_p, 1):
            print('{}. {: <20}: {} ({:.3} %)'.format(i, p, nbr_words_p[p], 100*nbr_words_p[p]/nbr_words))

        print('Top {} words: {}'.format(min(nbr_of_top_words, 10), list(top_words.keys())[:10]))
        for i, p in enumerate(top_words_p, 1):
            print('{}. {: <20}: {}'.format(i, p, list(top_words_p[p].keys())[:10]))
        
        print(banner('Characters'))
        print('Number of characters: {}'.format(nbr_characters))
        for i, p in enumerate(nbr_characters_p, 1):
            if nbr_characters_p[p] == 0:
                continue
            print('{}. {: <20}: {} ({:.3} %)'.format(i, p, nbr_characters_p[p], 100*nbr_characters_p[p]/nbr_characters))
        print('Top {} characters: {}'.format(nbr_of_top_characters, list(top_characters.keys())))

        print(banner('Averages'))
        print('Average length of messages: {} words'.format(fb.get_avg_len_msg()))
        print('Average length of messages: {:.1f} characters'.format(nbr_characters/nbr_messages))
        print('Average length of word: {:.1f} characters'.format(nbr_characters/nbr_words))
        for i, p in enumerate(nbr_words_p, 1):
            if nbr_words_p[p] == 0:
                continue
            print('{}. {: <20}: {:.1f} w/msg\t{:.1f} ch/msg\t{:.1f} ch/w'.format(i, p, nbr_words_p[p]/nbr_messages_p[p], nbr_characters_p[p]/nbr_messages_p[p], nbr_characters_p[p]/nbr_words_p[p]))
        print('Average messages per day: {}'.format(fb.get_avg_msg_day()))

        # Emojis
        print(banner('Emojis'))
        for i, p in enumerate(emojis_all_count, 1):
            if emojis_all_count[p] == 0:
                continue
            print('{}. {: <20}: {}'.format(i, p, emojis_all_count[p]))

        print('Top {} emojis: {}'.format(nbr_of_top_emojis, top_emojis))

        # Reactions emojis
        print(banner('Reactions emojis'))
        for i, p in enumerate(emojis_reactions_all_count, 1):
            if emojis_reactions_all_count[p] == 0:
                continue
            print('{}. {: <20}: {}'.format(i, p, emojis_reactions_all_count[p]))

        print('Top {} reactions emojis: {}'.format(nbr_of_top_emojis, top_reactions_emojis))

        # Generate PDF
        print(banner('Plots'))
        print('Generating PDF')

    pb = ProgressBar(12, prefix = fb.title, suffix = 'Complete', length = 50)
    if not print_in_terminal: pb.off()

    # Set appropriate filename
    names = ''
    if len(participants) > 2:
        names = 'Group chat: ' + fb.title
    else:
        for p in participants:
            names += p + ', '
        names = names[:-1]
    filename = fb.title + '.pdf'

    # Creating the results directory if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    with PdfPages(os.path.join('results', filename)) as pdf:
        #participants_on_plots = participants[:max_participants_on_plots] + (['Rest'] if len(participants) > max_participants_on_plots else [])

        # Plot participants messages percentage
        # Set a wider range of colors for the color cycle
        colors = plt.cm.tab20(np.linspace(0, 1, 20))
        plt.gca().set_prop_cycle('color', colors)
        fracs = [activity[act_p][0] for act_p in activity][:max_participants_on_plots]
        # Add the rest of the participants
        participants_on_plots = list(activity.keys())[:max_participants_on_plots] + (['Rest'] if len(participants) > max_participants_on_plots else [])
        if len(participants) > max_participants_on_plots:
            fracs.append(nbr_messages - sum(fracs))
        plt.pie(fracs, startangle=90, autopct='%1.1f%%')
        plt.legend(participants_on_plots,
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
        top_participants_in_words = fb.top_participants_in_words(max_participants_on_plots)
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
        top_participants_in_characters = fb.top_participants_in_characters(max_participants_on_plots)
        plt.pie(list(top_participants_in_characters.values()), startangle=90, autopct='%1.1f%%')
        plt.legend(list(top_participants_in_characters.keys()),
                   loc='upper left',
                   bbox_to_anchor=(-0.15, 1.15))
        plt.axis('equal')
        plt.title('Characters')
        pdf.savefig()
        plt.close()
        pb.printProgressBar()

        # Plot timeline
        months = nbr_days/30
        interval = int(round(months/12))
        fmt = mdates.DateFormatter('%Y-%m-%d')
        loc = mdates.MonthLocator(interval=interval)
        ax = plt.axes()
        ax.xaxis.set_major_formatter(fmt)
        plt.bar(timeline, nbr_times_day, align='center')
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
        plt.bar(hour, nbr_times_hour, align='center', width=0.8)
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
        plt.bar(weekday_arr, nbr_times_weekday, align='center', width=0.8)
        plt.xticks(weekday_arr, weekday_labels, rotation=30)
        plt.title('Activity by Weekday')
        plt.ylabel('Number of messages')
        plt.grid(True)
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        pb.printProgressBar()

        # Plot top emojis
        plt.rcParams['font.family'] = pdf_fonts
        plt.gca().set_prop_cycle('color', colors)

        x = np.arange(len(top_emojis))
        if len(participants) <= max_participants_on_plots:
            bar_width = 0.8 / len(participants)  # Calculate the width of each bar
    
            for i, participant in enumerate(participants):
                # Calculate the x values for the current participant
                x_offset = i * bar_width - (0.4 - bar_width / 2)
                plt.bar(x + x_offset, emoji_count_p[participant], align='center', width=bar_width, label=participant)
            plt.legend(list(emoji_count_p.keys()),
                   loc='upper left',
                   bbox_to_anchor=(-0.15, 1.15))
        else:
            plt.bar(x, [sum(val[i] for val in emoji_count_p.values()) for i in range(nbr_of_top_emojis)], align='center')

        plt.xticks(x, top_emojis)
        plt.title('Top {} emojis'.format(nbr_of_top_emojis))
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
        plt.rcParams['font.family'] = pdf_fonts
        plt.gca().set_prop_cycle('color', colors)

        x = np.arange(len(top_reactions_emojis))

        if len(participants) <= max_participants_on_plots:
            bar_width = 0.8 / len(participants)  # Calculate the width of each bar
    
            for i, participant in enumerate(participants):
                # Calculate the x values for the current participant
                x_offset = i * bar_width - (0.4 - bar_width / 2)
                plt.bar(x + x_offset, emoji_reactions_count_p[participant], align='center', width=bar_width, label=participant)
            plt.legend(list(emoji_reactions_count_p.keys()),
                   loc='upper left',
                   bbox_to_anchor=(-0.15, 1.15))
        else:
            plt.bar(x, [sum(val[i] for val in emoji_reactions_count_p.values()) for i in range(nbr_of_top_emojis)], align='center')
            

        plt.xticks(x, top_reactions_emojis)
        plt.title('Top {} reactions emojis'.format(nbr_of_top_emojis))
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
        fracs = [top_characters[c] for c in top_characters]
        # Add the percentage of the rest of the characters
        fracs.append(sum(list(top_characters.values())) - sum(fracs))
        plt.pie(fracs, startangle=90, autopct='%1.1f%%')
        plt.legend(list(top_characters.keys()) + ['Rest'],
                   loc='upper left',
                   bbox_to_anchor=(-0.15, 1.15))
        plt.axis('equal')
        plt.title('Top {} characters'.format(nbr_of_top_characters))
        pdf.savefig()
        plt.close()
        pb.printProgressBar()
        

        # Text statistics
        plt.rcParams['font.family'] = pdf_fonts
        plt.figure(figsize=(8.27, 11.69))
        plt.title('Text Statistics', fontsize=16, fontweight='bold')
        plt.axis('off')

        text_stats = [
            'Start: {}'.format(start),
            'End: {}'.format(end),
            'Number of days: {}'.format(nbr_days),
            'Number of days active: {} ({:.3} %)'.format(nbr_days_active, 100*nbr_days_active/nbr_days),
            'Most messages in one day: {}'.format(max(nbr_times_day)),
            'Number of messages: {}'.format(nbr_messages),
            'Number of words: {}'.format(nbr_words),
            'Number of characters: {}'.format(nbr_characters),
            'Top {} characters: {}'.format(nbr_of_top_characters, list(top_characters.keys())),
            'Average length of messages: {} words'.format(fb.get_avg_len_msg()),
            'Average length of messages: {:.1f} characters'.format(nbr_characters/nbr_messages),
            'Average length of word: {:.1f} characters'.format(nbr_characters/nbr_words),
            'Average messages per day: {}'.format(fb.get_avg_msg_day()),
        ]

        y = 1.0
        for elem in text_stats:
            plt.text(0.0, y, elem, fontsize=12, verticalalignment='center')
            y -= 0.025

        s = ""
        for i, p in enumerate(list(activity.keys())[:max_participants_on_plots], 1):
            s += '{}. {: <25}: {:2.1f} w/msg   {:2.1f} ch/msg   {:2.1f} ch/w'.format(i, p, nbr_words_p[p]/nbr_messages_p[p], nbr_characters_p[p]/nbr_messages_p[p], nbr_characters_p[p]/nbr_words_p[p]) + '\n'
            y -= 0.012
        plt.text(0.0, y, s, fontsize=12, verticalalignment='center')

        # Emojis
        s = f'Top {nbr_of_top_emojis} emojis: {top_emojis}\n'
        for i, p in enumerate(emojis_all_count, 1):
            if i > max_participants_on_plots:
                break
            if emojis_all_count[p] == 0:
                continue
            s += f'{i}. {p}: {emojis_all_count[p]}' + '\n'
        # Reactions emojis
        s += f'Top {nbr_of_top_emojis} reactions emojis: {top_reactions_emojis}\n'
        for i, p in enumerate(emojis_reactions_all_count, 1):
            if i > max_participants_on_plots:
                break
            if emojis_reactions_all_count[p] == 0:
                continue
            s += f'{i}. {p}: {emojis_reactions_all_count[p]}' + '\n'
        plt.text(0.0, 0.18, s, fontsize=12, verticalalignment='center')

        pdf.savefig()
        plt.close()
        pb.printProgressBar()

        # Top words
        plt.rcParams['font.family'] = pdf_fonts
        plt.figure(figsize=(8.27, 11.69))
        plt.title('Top words', fontsize=16, fontweight='bold')
        plt.axis('off')

        y = 0.95
        x = 0.0
        for j, word in enumerate(list(top_words.keys())):
                plt.text(x, y - 0.025*(j+1), '{}. {}: {}'.format(j+1, list(top_words.keys())[j], list(top_words.values())[j]), fontsize=12, verticalalignment='center')
        for i, p in enumerate(participants, 1):
            y = 0.95
            plt.text(x + 0.22*i, y, p.split()[0], fontsize=12, verticalalignment='center')
            for j, word in enumerate(list(top_words_p[p].keys()), 1):
                plt.text(x + 0.22*i, y - 0.025*j, '{}: {}'.format(word, top_words_p[p][word]), fontsize=12, verticalalignment='center')

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

    # Create a text file for better readability of statistics especialy for large groups chats
    txt_filename = fb.title + '.txt'
    txt_file_path = os.path.join('results', txt_filename)
    with open(txt_file_path, 'w', encoding='utf8') as txt:
        txt.write(banner('Times') + '\n')
        txt.write('Start: {}\nEnd: {}\n'.format(start, end))
        txt.write('Number of days: {}\n'.format(nbr_days))
        txt.write('Number of days active: {} ({:.3} %)\n'.format(nbr_days_active, 100*nbr_days_active/nbr_days))
        txt.write('Most messages in one day: {}\n'.format(max(nbr_times_day)))

        txt.write(banner('Messages') + '\n')
        txt.write('Number of messages: {}\n'.format(nbr_messages))
        for i, (act_p, data) in enumerate(activity.items(), 1):
            txt.write('{: >3}. {: <25}: {} ({:.3} %)\n'.format(i, act_p, data[0], data[1]))

        txt.write(banner('Words') + '\n')
        txt.write('Number of words: {}\n'.format(nbr_words))
        for i, p in enumerate(nbr_words_p, 1):
            txt.write('{: >3}. {: <25}: {} ({:.3} %)\n'.format(i, p, nbr_words_p[p], 100*nbr_words_p[p]/nbr_words))
        
        txt.write(banner('Characters') + '\n')
        txt.write('Number of characters: {}\n'.format(nbr_characters))
        txt.write('Top {} characters: {}\n'.format(nbr_of_top_characters, list(top_characters.keys())))
        for i, p in enumerate(nbr_characters_p, 1):
            txt.write('{: >3}. {: <25}: {} ({:.3} %)\n'.format(i, p, nbr_characters_p[p], 100*nbr_characters_p[p]/nbr_characters))

        txt.write(banner('Averages') + '\n')
        txt.write('Average length of messages: {} words\n'.format(fb.get_avg_len_msg()))
        txt.write('Average length of messages: {:.1f} characters\n'.format(nbr_characters/nbr_messages))
        txt.write('Average length of word: {:.1f} characters\n'.format(nbr_characters/nbr_words))
        for i, p in enumerate(nbr_words_p, 1):
            txt.write('{: >3}. {: <25}: {:.1f} w/msg\t{:.1f} ch/msg\t{:.1f} ch/w\n'.format(i, p, nbr_words_p[p]/nbr_messages_p[p], nbr_characters_p[p]/nbr_messages_p[p], nbr_characters_p[p]/nbr_words_p[p]))
        txt.write('Average messages per day: {}\n'.format(fb.get_avg_msg_day()))

        # Emojis
        txt.write(banner('Emojis') + '\n')
        txt.write('Top {} emojis: {}\n'.format(nbr_of_top_emojis, top_emojis))
        for i, p in enumerate(emojis_all_count, 1):
            txt.write('{: >3}. {: <25}: {}\n'.format(i, p, emojis_all_count[p]))

        # Reactions emojis
        txt.write(banner('Reactions emojis') + '\n')
        txt.write('Top {} reactions emojis: {}\n'.format(nbr_of_top_emojis, top_reactions_emojis))
        for i, p in enumerate(emojis_reactions_all_count, 1):
            txt.write('{: >3}. {: <25}: {}\n'.format(i, p, emojis_reactions_all_count[p]))

        txt.write(banner('Top words') + '\n')
        if len(participants) <= 10:
            column_width = 25
            for i in range(0, len(participants) + 1):
                if i == 0:
                    txt.write('Top words'.ljust(column_width))
                else:
                    txt.write((str(i) + '. ' + participants[i-1]).ljust(column_width))
            txt.write('\n')
            for i in range(len(list(top_words.keys()))):
                txt.write('{}. {} ({})'.format(i + 1, list(top_words.keys())[i], list(top_words.values())[i]).ljust(column_width))
                for j, p in enumerate(top_words_p, 1):
                    if i < len(list(top_words_p[p].keys())):
                        txt.write('{} ({})'.format(list(top_words_p[p].keys())[i], list(top_words_p[p].values())[i]).ljust(column_width))
                    else:
                        txt.write(' '.ljust(column_width))
                txt.write('\n')
        else:
            #Writing with tabulation for importing to excel
            for i in range(0, len(participants) + 1):
                if i == 0:
                    txt.write('Top words\t')
                else:
                    txt.write((str(i) + '. ' + participants[i-1]) + '\t')
            txt.write('\n')
            for i in range(nbr_of_top_words):
                txt.write('{}. {} ({})'.format(i + 1, list(top_words.keys())[i], list(top_words.values())[i]) + '\t')
                for j, p in enumerate(top_words_p, 1):
                    if i < len(list(top_words_p[p].keys())):
                        txt.write('{} ({})'.format(list(top_words_p[p].keys())[i], list(top_words_p[p].values())[i]) + '\t')
                    else:
                        txt.write(' \t')
                txt.write('\n')

    if print_in_terminal: print('\ntxt \'{}\' generated successfully!'.format(txt_filename))

    if not print_in_terminal:
        print('{} PDF and txt files generated successfully!'.format(fb.title))


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
