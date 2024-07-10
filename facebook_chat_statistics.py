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
    if len(sys.argv) == 2:
         path_to_conversation = str(sys.argv[1])
    else:
        print('Usage: python3 {} chats/Conversation.json'
        .format(sys.argv[0]))
        sys.exit()

    fb = FacebookMessengerConversation(path_to_conversation)
    nbr_of_top_emojis = 10
    nbr_of_top_characters = 10
    nbr_of_top_words = 20

    participants = fb.get_participants()

    print(banner('Times'))
    start, end = fb.get_time_interval('str')
    print('Start: {}\nEnd: {}'.format(start, end))
    nbr_days = fb.get_nbr_days()
    print('Number of days: {}'.format(nbr_days))
    timeline, nbr_times_day, nbr_times_weekday, nbr_times_hour = fb.timeline()
    print('Most messages in one day: {}'.format(max(nbr_times_day)))

    print(banner('Messages'))
    nbr_messages = fb.get_nbr_msg()
    print('Number of messages: {}'.format(nbr_messages))
    activity = fb.activity()
    for i, (act_p, data) in enumerate(activity.items(), 1):
        print('{}. {}: {} ({:.3} %)'.format(i, act_p, data[0], data[1]))

    print(banner('Words'))
    nbr_words = fb.get_nbr_words()
    print('Number of words: {}'.format(nbr_words))
    nbr_words_p = fb.get_nbr_words_p()
    for i, p in enumerate(participants, 1):
        print('{}. {}: {} ({:.3} %)'.format(i, p, nbr_words_p[p], 100*nbr_words_p[p]/nbr_words))
    top_words = fb.top_words(nbr_of_top_words)
    print('Top {} words: {}'.format(nbr_of_top_words, list(top_words.keys())))
    top_words_p = fb.top_words_p(nbr_of_top_words)
    for i, p in enumerate(participants, 1):
        print('{}. {}: {}'.format(i, p, list(top_words_p[p].keys())))
    
    print(banner('Characters'))
    nbr_characters_p = fb.get_nbr_characters_p()
    nbr_characters = sum(nbr_characters_p.values())
    print('Number of characters: {}'.format(nbr_characters))
    for i, p in enumerate(participants, 1):
        print('{}. {}: {} ({:.3} %)'.format(i, p, nbr_characters_p[p], 100*nbr_characters_p[p]/nbr_characters))
    top_characters = fb.top_characters(nbr_of_top_characters)
    print('Top {} characters: {}'.format(nbr_of_top_characters, list(top_characters.keys())))

    print(banner('Averages'))
    print('Average length of messages: {} words'.format(fb.get_avg_len_msg()))
    print('Average length of messages: {:.1f} characters'.format(nbr_characters/nbr_messages))
    print('Average length of word: {:.1f} characters'.format(nbr_characters/nbr_words))
    print('Average messages per day: {}'.format(fb.get_avg_msg_day()))

    # Emojis
    print(banner('Emojis'))
    top_emojis, emoji_count_p, emojis_all_count = fb.top_emojis(nbr_of_top_emojis)
    for i, p in enumerate(participants, 1):
        print('{}. {}:\t{}'.format(i, p, emojis_all_count[p]))

    print('Top {} emojis: {}'.format(nbr_of_top_emojis, top_emojis))

    # Reactions emojis
    print(banner('Reactions emojis'))
    top_reactions_emojis, emoji_reactions_count_p, emojis_reactions_all_count = fb.top_reactions_emojis(nbr_of_top_emojis)
    for i, p in enumerate(participants, 1):
        print('{}. {}:\t{}'.format(i, p, emojis_reactions_all_count[p]))

    print('Top {} reactions emojis: {}'.format(nbr_of_top_emojis, top_reactions_emojis))

    # Generate PDF
    print(banner('Plots'))
    print('Generating PDF')
    pb = ProgressBar(12, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Set appropriate filename
    names = ''
    for p in participants:
        name = p.split(' ')
        names += '{}_{}_'.format(name[0], name[1])
    names = names[:-1]
    filename = os.path.splitext(os.path.basename(sys.argv[1]))[0] + '.pdf'

    with PdfPages(os.path.join('results', filename)) as pdf:
        # Plot participants messages percentage
        # Set a wider range of colors for the color cycle
        colors = plt.cm.tab20(np.linspace(0, 1, 20))
        plt.gca().set_prop_cycle('color', colors)
        fracs = [activity[act_p][0] for act_p in activity]
        plt.pie(fracs, startangle=90, autopct='%1.1f%%')
        plt.legend(participants,
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
        fracs = [100*nbr_words_p[p]/nbr_words for p in participants]
        plt.pie(fracs, startangle=90, autopct='%1.1f%%')
        plt.legend(participants,
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
        fracs = [100*nbr_characters_p[p]/nbr_characters for p in participants]
        plt.pie(fracs, startangle=90, autopct='%1.1f%%')
        plt.legend(participants,
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
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
        plt.gca().set_prop_cycle('color', colors)

        x = np.arange(len(top_emojis))
        bar_width = 0.8 / len(participants)  # Calculate the width of each bar

        for i, participant in enumerate(participants):
            # Calculate the x values for the current participant
            x_offset = i * bar_width - (0.4 - bar_width / 2)
            plt.bar(x + x_offset, emoji_count_p[participant], align='center', width=bar_width, label=participant)

        plt.xticks(x, top_emojis)
        plt.title('Top {} emojis'.format(nbr_of_top_emojis))
        plt.ylabel('Number of times used')
        plt.legend()
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
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
        plt.gca().set_prop_cycle('color', colors)

        x = np.arange(len(top_reactions_emojis))
        bar_width = 0.8 / len(participants)  # Calculate the width of each bar

        for i, participant in enumerate(participants):
            # Calculate the x values for the current participant
            x_offset = i * bar_width - (0.4 - bar_width / 2)
            plt.bar(x + x_offset, emoji_reactions_count_p[participant], align='center', width=bar_width, label=participant)

        plt.xticks(x, top_reactions_emojis)
        plt.title('Top {} reactions emojis'.format(nbr_of_top_emojis))
        plt.ylabel('Number of times used')
        plt.legend()
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
        fracs = [100*top_characters[c]/nbr_characters for c in top_characters]
        # Add the percentage of the rest of the characters
        fracs.append(100 - sum(fracs))
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
        plt.rcParams['font.family'] = ['Arial', 'Segoe UI Emoji']
        plt.figure(figsize=(8.27, 11.69))
        plt.title('Text Statistics', fontsize=16, fontweight='bold')
        plt.axis('off')

        text_stats = [
            'Start: {}'.format(start),
            'End: {}'.format(end),
            'Number of days: {}'.format(nbr_days),
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

        emoji_stats = [
            'Top {} emojis: {}'.format(nbr_of_top_emojis, top_emojis),
            'Top {} reactions emojis: {}'.format(nbr_of_top_emojis, top_reactions_emojis)
        ]

        y = 0.95
        for elem in text_stats:
            plt.text(0.0, y, elem, fontsize=12, verticalalignment='center')
            y -= 0.025
        
        for elem in emoji_stats:
            plt.text(0.0, y, elem, fontsize=12, verticalalignment='center')
            y -= 0.07

        pdf.savefig()
        plt.close()
        pb.printProgressBar()

        # Top words
        plt.rcParams['font.family'] = ['Arial', 'Segoe UI Emoji']
        plt.figure(figsize=(8.27, 11.69))
        plt.title('Top words', fontsize=16, fontweight='bold')
        plt.axis('off')

        y = 0.95
        x = 0.0
        for j, word in enumerate(list(top_words.keys())):
                plt.text(x, y - 0.025*(j+1), '{}. {}: {}'.format(j+1, list(top_words.keys())[j], list(top_words.values())[j]), fontsize=12, verticalalignment='center')
        for i, p in enumerate(participants, 1):
            y = 0.95
            plt.text(x + 0.2*i, y, p.split()[0], fontsize=12, verticalalignment='center')
            for j, word in enumerate(list(top_words_p[p].keys()), 1):
                plt.text(x + 0.2*i, y - 0.025*j, '{}: {}'.format(word, top_words_p[p][word]), fontsize=12, verticalalignment='center')

        pdf.savefig()
        plt.close()
        pb.printProgressBar()

        # PDF info
        d = pdf.infodict()
        d['Title'] = filename.replace('_', ' ')
        d['Author'] = 'Facebook Chat Statistics'
        d['Subject'] = 'Conversation statistics between {}'.format(
            names.replace('_', ' '))
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.today()

    pb.printProgressBar()
    print('\nPDF generated successfully!')


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
