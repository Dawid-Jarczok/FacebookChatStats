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

    participants = fb.get_participants()

    print(banner('Times'))
    start, end = fb.get_time_interval('str')
    print('Start: {}\nEnd: {}'.format(start, end))

    print(banner('Totals'))
    activity = fb.activity()
    for act_p in activity:
        print('Number of messages {}: {} ({} %)'.format(act_p,
                                                        activity[act_p][0],
                                                        activity[act_p][1]))
    nbr_days = fb.get_nbr_days()
    print('Number of days: {}'.format(nbr_days))
    print('Number of messages: {}'.format(fb.get_nbr_msg()))
    print('Number of words: {}'.format(fb.get_nbr_words()))

    print(banner('Averages'))
    print('Average length of messages: {} words'.format(fb.get_avg_len_msg()))
    print('Average messages per day: {}'.format(fb.get_avg_msg_day()))

    print(banner('Plots'))

    # Set appropriate filename
    names = ''
    for p in participants:
        name = p.split(' ')
        names += '{}_{}_'.format(name[0], name[1])
    names = names[:-1]
    filename = os.path.splitext(os.path.basename(sys.argv[1]))[0] + '.pdf'

    # Generate PDF
    with PdfPages(os.path.join('results', filename)) as pdf:
        # Plot percentage
        # Set a wider range of colors for the color cycle
        colors = plt.cm.tab20(np.linspace(0, 1, 20))
        plt.gca().set_prop_cycle('color', colors)
        fracs = [activity[act_p][0] for act_p in activity]
        plt.pie(fracs, startangle=90, autopct='%1.1f%%')
        plt.legend(participants,
                   loc='upper left',
                   bbox_to_anchor=(-0.15, 1.15))
        plt.axis('equal')
        plt.title('Who texts the most?')
        pdf.savefig()
        plt.close()

        # Plot timeline
        timeline, nbr_times_day, nbr_times_weekday, nbr_times_hour = fb.timeline()
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

        # Plot top emojis
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
        plt.gca().set_prop_cycle('color', colors)

        top_emojis, emoji_count_p = fb.top_emojis(nbr_of_top_emojis)
        x = np.arange(len(top_emojis))
        bar_width = 0.8 / len(participants)  # Calculate the width of each bar

        for i, participant in enumerate(participants):
            # Calculate the x values for the current participant
            x_offset = i * bar_width - (0.4 - bar_width / 2)
            plt.bar(x + x_offset, emoji_count_p[participant], align='center', width=bar_width, label=participant)

        plt.xticks(x, top_emojis)
        plt.title('Top 10 emojis')
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

        # PDF info
        d = pdf.infodict()
        d['Title'] = filename.replace('_', ' ')
        d['Author'] = 'Facebook Chat Statistics'
        d['Subject'] = 'Conversation statistics between {}'.format(
            names.replace('_', ' '))
        d['CreationDate'] = datetime.today()
        d['ModDate'] = datetime.today()

    print('Most messages in one day: {}'.format(max(nbr_times_day)))
    print('Top 10 emojis: {}'.format(top_emojis))
    print('PDF generated successfully!')


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
