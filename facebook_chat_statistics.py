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

warnings.filterwarnings('ignore', module='matplotlib')

class FacebookChatStatistics(FacebookMessengerConversation):

    def __init__(self, path_to_conversation):
        super().__init__(path_to_conversation, 10, 40, 10)
        self.max_participants_on_plots = 10
        self.pdf_fonts = ['Arial', 'Segoe UI Emoji']


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
        print('Number of active days: {} ({:.3} %)'.format(self.nbr_days_active, 100*self.nbr_days_active/self.nbr_days))
        print('Number of active days in row: {} ({} : {})'.format(self.nbr_days_active_in_row, self.time_start_days_active_in_row_str, self.time_end_days_active_in_row_str))
        print('Number of inactive days in row: {} ({} : {})'.format(self.nbr_days_inactive_in_row, self.time_start_days_inactive_in_row_str, self.time_end_days_inactive_in_row_str))
        print('Most messages in one day: {}'.format(max(self.nbr_times_day)))

        print(banner('Messages'))
        print('Number of messages: {}'.format(self.nbr_msg))
        print(get_stats(self.nbr_msg_p, self.nbr_msg))

        print(banner('Words'))
        print('Number of words: {}'.format(self.nbr_words))
        print(get_stats(self.nbr_words_p, self.nbr_words))

        print('Top {} words: {}'.format(min(self.nbr_top_words, 10), list(self.top_words.keys())[:10]))
        for i, p in enumerate(self.top_words_p, 1):
            print('{}. {: <20}: {}'.format(i, p, list(self.top_words_p[p].keys())[:10]))
        
        print(banner('Characters'))
        print('Number of characters: {}'.format(self.nbr_chars))
        print(get_stats(self.nbr_chars_p, self.nbr_chars))
        print('Top {} characters: {}'.format(self.nbr_top_characters, list(self.top_chars.keys())[:self.nbr_top_characters]))

        print(banner('Averages'))
        print('Average messages per day: {:.1f}'.format(self.avg_msg_per_day))
        print('Average length of messages: {:.1f} words'.format(self.avg_words_per_msg))
        print('Average length of messages: {:.1f} characters'.format(self.avg_chars_per_msg))
        print('Average length of word: {:.1f} characters'.format(self.avg_chars_per_word))
        print('Average reply time: {:.1f} seconds ({:.0f}h {:.0f}min)'.format(self.avg_reply_time, self.avg_reply_time // 3600, (self.avg_reply_time % 3600) // 60))
        print('Median reply time: {:.1f} seconds'.format(self.median_reply_time))
        print('   {: <20} {: >12} {: >12} {: >15} {: >18} {: >18}'.format('Participant', 'Words/msg', 'Chars/msg', 'Chars/word', 'Avg reply time', 'Median reply time'))
        for i, p in enumerate(self.nbr_words_p, 1):
            if len(self.p) > 10 and self.nbr_words_p[p] == 0:
                continue
            print('{}. {: <20}: {:>5.1f} w/msg{:>8.1f} ch/msg{:>7.1f} ch/w{:>11.0f} s{:>13.0f} s'.format(
                i, p, self.avg_words_per_msg_p[p], self.avg_chars_per_msg_p[p], self.avg_chars_per_word_p[p], self.avg_reply_time_p[p], self.median_reply_time_p[p]))

        print(banner('Edits'))
        print('Number of editions: {}'.format(self.nbr_editions))
        if self.nbr_editions: print(get_stats(self.nbr_editions_p, self.nbr_editions))

        print(banner('Unsent messages'))
        print('Number of unsent messages: {}'.format(self.nbr_unsent_msg))
        if self.nbr_unsent_msg: print(get_stats(self.nbr_unsent_msg_p, self.nbr_unsent_msg))

        print(banner('Photos'))
        print('Number of photos: {}'.format(self.nbr_photos))
        if self.nbr_photos: print(get_stats(self.nbr_photos_p, self.nbr_photos))

        print(banner('Videos'))
        print('Number of videos: {}'.format(self.nbr_videos))
        if self.nbr_videos: print(get_stats(self.nbr_videos_p, self.nbr_videos))

        print(banner('Gifs'))
        print('Number of gifs: {}'.format(self.nbr_gifs))
        if self.nbr_gifs: print(get_stats(self.nbr_gifs_p, self.nbr_gifs))

        print(banner('Stickers'))
        print('Number of stickers: {}'.format(self.nbr_stickers))
        if self.nbr_stickers: print(get_stats(self.nbr_stickers_p, self.nbr_stickers))

        print(banner('Files'))
        print('Number of files: {}'.format(self.nbr_files))
        if self.nbr_files: print(get_stats(self.nbr_files_p, self.nbr_files))

        print(banner('Audio'))
        print('Number of audio: {}'.format(self.nbr_audio))
        if self.nbr_audio: print(get_stats(self.nbr_audio_p, self.nbr_audio))

        print(banner('Shares'))
        print('Number of shares: {}'.format(self.nbr_shares))
        if self.nbr_shares: print(get_stats(self.nbr_shares_p, self.nbr_shares))


        # Emojis
        print(banner('Emojis'))
        print('Number of emojis: {}'.format(sum(self.emojis_all_count.values())))
        print(get_stats(self.emojis_all_count, sum(self.emojis_all_count.values())))
        print('Top {} emojis: {}'.format(self.nbr_top_emojis, list(self.top_emojis.keys())))

        # Reactions emojis
        print(banner('Reactions emojis'))
        print('Number of reactions emojis: {}'.format(sum(self.emojis_reactions_all_count.values())))
        print(get_stats(self.emojis_reactions_all_count, sum(self.emojis_reactions_all_count.values())))
        print('Top {} reactions emojis: {}'.format(self.nbr_top_emojis, list(self.top_reactions_emojis.keys())))

    def generate_pdf(self, print_in_terminal=False):
        pb = ProgressBar(27, prefix = self.title, suffix = 'Complete', length = 50)
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

            figsize = {'pie' : (6.4, 4.8), 'bar' : (8.0, 4.8), 'text' : (8.27, 11.69)}
            plt.rcParams['font.family'] = self.pdf_fonts
            plt.rcParams['figure.figsize'] = figsize['pie']
            colors = plt.cm.tab10(np.linspace(0, 1, 10))

            # Plot participants messages percentage
            create_pie_chart_with_rest('Messages', self.nbr_msg_p.values(), self.nbr_msg_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot participants words percentage
            create_pie_chart_with_rest('Words', self.nbr_words_p.values(), self.nbr_words_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot participants characters percentage
            create_pie_chart_with_rest('Characters', self.nbr_chars_p.values(), self.nbr_chars_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot unsent messages
            if self.nbr_unsent_msg:
                create_pie_chart_with_rest('Unsent messages', self.nbr_unsent_msg_p.values(), self.nbr_unsent_msg_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot photos
            if self.nbr_photos:
                create_pie_chart_with_rest('Photos', self.nbr_photos_p.values(), self.nbr_photos_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot videos
            if self.nbr_videos:
                create_pie_chart_with_rest('Videos', self.nbr_videos_p.values(), self.nbr_videos_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot gifs
            if self.nbr_gifs:
                create_pie_chart_with_rest('Gifs', self.nbr_gifs_p.values(), self.nbr_gifs_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot stickers
            if self.nbr_stickers:
                create_pie_chart_with_rest('Stickers', self.nbr_stickers_p.values(), self.nbr_stickers_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot files
            if self.nbr_files:
                create_pie_chart_with_rest('Files', self.nbr_files_p.values(), self.nbr_files_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot audio
            if self.nbr_audio:
                create_pie_chart_with_rest('Audio', self.nbr_audio_p.values(), self.nbr_audio_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            # Plot shares
            if self.nbr_shares:
                create_pie_chart_with_rest('Shares', self.nbr_shares_p.values(), self.nbr_shares_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            
            # For now only user have recorded editions so plot has no sense
            # Older versions of the chat do not have editions
            if False and self.nbr_editions > 0:
                # Plot participants editions percentage
                create_pie_chart_with_rest('Editions', self.nbr_editions_p.values(), self.nbr_editions_p.keys(), self.max_participants_on_plots, pdf)
            pb.printProgressBar()

            plt.rcParams['figure.figsize'] = figsize['bar']
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

            # Plot activity timeline
            fmt = mdates.DateFormatter('%Y-%m-%d')
            ax = plt.axes()
            ax.xaxis.set_major_formatter(fmt)
            plt.plot(self.timeline, self.activity_timeline)
            plt.title('Active days timeline')
            plt.ylabel('Percentage')
            plt.ylim(top=1)
            plt.yticks(plt.yticks()[0], ['{:,.0%}'.format(x) for x in plt.yticks()[0]])
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


            plt.gca().set_prop_cycle('color', colors)

            # Plot reply times
            # Plot reply times #2 is better
            """intervals = [10, 30, 60, 300, 900, 3600, 43200, 86400, 864000]
            intervals_labels = ['0s-10s', '10s-30s', '30s-1min', '1min-5min', '5min-15min', '15min-1h', '1h-12h', '12h-1day', '>1day']
            j = 0
            val = {}
            x = np.arange(len(intervals))
            if len(self.p) <= self.max_participants_on_plots:
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
                for k, p in enumerate(self.p):
                    j = 0
                    # Calculate the x values for the current participant
                    x_offset = k * bar_width - (0.4 - bar_width / 2)
                    val.update({p : [0 for i in intervals]})
                    for i in reversed(self.reply_times_p[p]):
                        if i > intervals[j] and j < len(intervals) - 1:
                            j += 1
                        val[p][j] += 1
                    #plt.bar(x + x_offset, val[p], align='center', width=bar_width, label=p)
                    plt.plot(x, val[p], label=p)
                plt.legend(self.p,
                        loc='upper right',
                        bbox_to_anchor=(1.15, 1.15))
            else:
                val = [0 for i in intervals]
                for i in reversed(self.reply_times):
                    if i > intervals[j] and j < len(intervals) - 1:
                        j += 1
                    val[j] += 1
                plt.bar(x, val, align='center', width=0.8)

            plt.xticks(x, intervals_labels, rotation=10)
            plt.title('Reply times')
            plt.ylabel('Number of messages')
            plt.grid(True)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot reply times (participant percentage share)
            if len(self.p) <= self.max_participants_on_plots:
                val_sum = [0 for i in intervals]
                for p in self.p:
                    for i in range(len(intervals)):
                        val_sum[i] += val[p][i]

                for k, p in enumerate(self.p):
                    # Calculate the x values for the current participant
                    x_offset = k * bar_width - (0.4 - bar_width / 2)
                    v = [x / val_sum[k] if val_sum[k] != 0 else 0 for k, x in enumerate(val[p])]
                    #plt.bar(x + x_offset, v, align='center', width=bar_width, label=p)
                    plt.plot(x, v, label=p)

                plt.legend(self.p, loc='upper right', bbox_to_anchor=(1.15, 1.15))
                plt.xticks(x, intervals_labels, rotation=10)
                plt.title('Reply times')
                plt.ylabel('Percentage of messages')
                plt.yticks(plt.yticks()[0], ['{:,.0%}'.format(x) for x in plt.yticks()[0]])
                plt.grid(True)
                plt.tight_layout()
                pdf.savefig()
                plt.close()
            pb.printProgressBar()"""


            # Plot reply times #2
            intervals = [1.0 * (1.294 ** i) for i in range(45)]
            def custom_ftm(x, pos):
                h = x // 3600
                m = x % 3600 // 60
                s = x % 3600 % 60
                if h == 0:
                    if m == 0:
                        return '{:2.0f}s'.format(s)
                    return '{:2.0f}min'.format(x // 60)
                return '{:2.0f}h'.format(x // 3600)
            
            j = 0
            val = {}
            x = np.arange(len(intervals))
            if len(self.p) <= self.max_participants_on_plots:
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
                for k, p in enumerate(self.p):
                    j = 0
                    # Calculate the x values for the current participant
                    #x_offset = k * bar_width - (0.4 - bar_width / 2)
                    val.update({p : [0 for i in intervals]})
                    for i in reversed(self.reply_times_p[p]):
                        if i > intervals[j] and j < len(intervals) - 1:
                            j += 1
                        val[p][j] += 1
                    #plt.bar(x + x_offset, val[p], align='center', width=bar_width, label=p)
                    plt.plot(x, val[p], label=p)
                plt.legend(self.p, loc='upper right', bbox_to_anchor=(1.15, 1.15))
            else:
                val = [0 for i in intervals]
                for i in reversed(self.reply_times):
                    if i > intervals[j] and j < len(intervals) - 1:
                        j += 1
                    val[j] += 1
                #plt.bar(x, val, align='center', width=0.8)
                plt.plot(x, val)

            #plt.xticks(x, intervals_labels, rotation=10)
            plt.xticks([i for i in range(0, len(intervals), 4)], [custom_ftm(i, 0) for i in intervals[::4]])
            plt.title('Reply times')
            plt.ylabel('Number of messages')
            plt.grid(True)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot reply times (participant percentage share)
            # Not necessary, previous plot is enough
            """if len(self.p) <= self.max_participants_on_plots and self.nbr_msg > 1000:
                val_sum = [0 for i in intervals]
                for p in self.p:
                    for i in range(len(intervals)):
                        val_sum[i] += val[p][i]

                for k, p in enumerate(self.p):
                    # Calculate the x values for the current participant
                    #x_offset = k * bar_width - (0.4 - bar_width / 2)
                    v = [x / val_sum[k] if val_sum[k] != 0 else 0 for k, x in enumerate(val[p])]
                    #plt.bar(x + x_offset, v, align='center', width=bar_width, label=p)
                    plt.plot(x, v, label=p)

                plt.legend(self.p, loc='upper right', bbox_to_anchor=(1.15, 1.15))
                #plt.xticks(x, intervals_labels, rotation=10)
                plt.xticks([i for i in range(0, len(intervals), 4)], [custom_ftm(i, 0) for i in intervals[::4]])
                plt.title('Reply times')
                plt.ylabel('Percentage of messages')
                plt.yticks(plt.yticks()[0], ['{:,.0%}'.format(x) for x in plt.yticks()[0]])
                plt.grid(True)
                plt.tight_layout()
                pdf.savefig()
                plt.close()"""


            # Plot messages per day
            intervals = [0, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 100000]
            intervals_labels = ['0', '1-10', '10-25', '25-50', '50-100', '100-250', '250-500', '500-1000', '1000-2500', '2500-5000', '5000-10000', '>10000']
            j = 0
            val = [0 for i in intervals]
            for i in sorted(self.nbr_times_day, reverse=False):
                if i > intervals[j] and j < len(intervals) - 1:
                    j += 1
                val[j] += 1

            while val[-1] == 0:
                val.pop()
                intervals_labels.pop()
            val.pop(0)
            intervals_labels.pop(0)
            x = np.arange(len(val))
            plt.bar(x, val, align='center', width=0.8)
            plt.xticks(x, intervals_labels, rotation=0)
            plt.title('Days per number of messages')
            plt.ylabel('Number of days')
            plt.xlabel('Number of messages')
            plt.grid(True)
            plt.tight_layout()
            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Plot number of messages in a row
            plt.gca().set_prop_cycle('color', colors)
            if len(self.p) <= self.max_participants_on_plots:
                intervals_labels = [str(i) for i in self.nbr_msg_in_row_p[self.p[0]].keys()]
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
                x = np.arange(len(intervals_labels))
                for k, p in enumerate(self.p):
                    j = 0
                    # Calculate the x values for the current participant
                    x_offset = k * bar_width - (0.4 - bar_width / 2)
                    plt.bar(x + x_offset, self.nbr_msg_in_row_p[p].values(), align='center', width=bar_width, label=p)
                plt.legend(self.p,
                        loc='upper right',
                        bbox_to_anchor=(1.15, 1.15))
                plt.xticks(x, intervals_labels, rotation=0)
                plt.title('Messages in a row')
                plt.xlabel('Number of messages in a row')
                plt.ylabel('Count')
                #plt.yscale('log')
                plt.grid(True)
                plt.tight_layout()
                pdf.savefig()
                plt.close()
            pb.printProgressBar()

            # Plot number of messages in a row (participant percentage share)
            if len(self.p) <= self.max_participants_on_plots:
                val_sum = [0 for i in self.nbr_msg_in_row_p[p].values()]
                for p in self.p:
                    for i, elem in enumerate(self.nbr_msg_in_row_p[p].values()):
                        val_sum[i] += elem

                for k, p in enumerate(self.p):
                    # Calculate the x values for the current participant
                    x_offset = k * bar_width - (0.4 - bar_width / 2)
                    v = [x / val_sum[k] if val_sum[k] != 0 else 0 for k, x in enumerate(self.nbr_msg_in_row_p[p].values())]
                    plt.bar(x + x_offset, v, align='center', width=bar_width, label=p)

                plt.legend(self.p, loc='upper right', bbox_to_anchor=(1.15, 1.15))
                plt.xticks(x, intervals_labels, rotation=10)
                plt.title('Messages in a row')
                plt.xlabel('Number of messages in a row')
                plt.ylabel('Percentage')
                plt.yticks(plt.yticks()[0], ['{:,.0%}'.format(x) for x in plt.yticks()[0]])
                plt.grid(True)
                plt.tight_layout()
                pdf.savefig()
                plt.close()
            pb.printProgressBar()

            # Plot top emojis
            plt.gca().set_prop_cycle('color', colors)

            x = np.arange(len(self.top_emojis))
            if len(self.p) <= self.max_participants_on_plots:
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
        
                for i, participant in enumerate(self.emojis_all_count.keys()):
                    # Calculate the x values for the current participant
                    x_offset = i * bar_width - (0.4 - bar_width / 2)
                    plt.bar(x + x_offset, [self.top_emojis[emoji_key][participant] for emoji_key in self.top_emojis], align='center', width=bar_width, label=participant)
                plt.legend(self.emojis_all_count.keys(),
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
            plt.gca().set_prop_cycle('color', colors)

            x = np.arange(len(self.top_reactions_emojis))
            if len(self.p) <= self.max_participants_on_plots:
                bar_width = 0.8 / len(self.p)  # Calculate the width of each bar
        
                for i, participant in enumerate(self.emojis_reactions_all_count.keys()):
                    # Calculate the x values for the current participant
                    x_offset = i * bar_width - (0.4 - bar_width / 2)
                    plt.bar(x + x_offset, [self.top_reactions_emojis[emoji_key][participant] for emoji_key in self.top_reactions_emojis], align='center', width=bar_width, label=participant)
                plt.legend(self.emojis_reactions_all_count.keys(),
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
            
            # Plot top characters
            plt.rcParams['figure.figsize'] = figsize['pie']
            create_pie_chart_with_rest('Top {} characters'.format(self.nbr_top_characters), list(self.top_chars.values()), list(self.top_chars.keys()), self.nbr_top_characters, pdf)
            pb.printProgressBar()
            

            plt.rcParams['figure.figsize'] = figsize['text']
            # Text statistics 1
            plt.title('Text Statistics', fontsize=16, fontweight='bold')
            plt.axis('off')

            text_stats = [
                'Start: {}'.format(self.time_start_str),
                'End: {}'.format(self.time_end_str),
                'Number of days: {}'.format(self.nbr_days),
                'Number of active days: {} ({:.3} %)'.format(self.nbr_days_active, 100*self.nbr_days_active/self.nbr_days),
                'Number of active days in row: {} ({} : {})'.format(self.nbr_days_active_in_row, self.time_start_days_active_in_row_str, self.time_end_days_active_in_row_str),
                'Number of inactive days in row: {} ({} : {})'.format(self.nbr_days_inactive_in_row, self.time_start_days_inactive_in_row_str, self.time_end_days_inactive_in_row_str),
                'Most messages in one day: {}'.format(max(self.nbr_times_day)),
                'Number of messages: {}'.format(self.nbr_msg),
                'Number of words: {}'.format(self.nbr_words),
                'Number of characters: {}'.format(self.nbr_chars),
                'Top {} characters: {}'.format(self.nbr_top_characters, list(self.top_chars.keys())[:self.nbr_top_characters]),
                '',
                'Average length of messages: {:.1f} words'.format(self.avg_words_per_msg),
                'Average length of messages: {:.1f} characters'.format(self.avg_chars_per_msg),
                'Average length of word: {:.1f} characters'.format(self.avg_chars_per_word),
                'Average messages per day: {:.1f}'.format(self.avg_msg_per_day),
                'Average reply time: {:.1f} seconds ({:.0f}h {:.0f}min) (rejecting >1day)'.format(self.avg_reply_time, self.avg_reply_time // 3600, (self.avg_reply_time % 3600) // 60),
                'Median reply time: {:.1f} seconds'.format(self.median_reply_time),
                '',
                'Number of unsent messages: {}'.format(self.nbr_unsent_msg),
                'Number of editions: {}'.format(self.nbr_editions),
                'Number of photos: {}'.format(self.nbr_photos),
                'Number of videos: {}'.format(self.nbr_videos),
                'Number of gifs: {}'.format(self.nbr_gifs),
                'Number of stickers: {}'.format(self.nbr_stickers),
                'Number of files: {}'.format(self.nbr_files),
                'Number of audio: {}'.format(self.nbr_audio),
                'Number of shares: {}'.format(self.nbr_shares),
            ]

            y = 1.0
            for elem in text_stats:
                plt.text(0.0, y, elem, fontsize=12, verticalalignment='center')
                y -= 0.025

            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Text statistics 2
            plt.axis('off')
            text_stats = []
            # Participants averages
            text_stats.append('   {: <20} {: >12} {: >12} {: >15} {: >18} {: >18}'.format('Participant', 'Words/msg', 'Chars/msg', 'Chars/word', 'Avg reply time', 'Median reply time'))
            for i, p in enumerate(list(self.nbr_msg_p.keys())[:self.max_participants_on_plots], 1):
                text_stats.append('{}. {: <20}: {:>5.1f} w/msg{:>8.1f} ch/msg{:>7.1f} ch/w{:>11.0f} s{:>13.0f} s'.format(
                    i, p, self.avg_words_per_msg_p[p], self.avg_chars_per_msg_p[p], self.avg_chars_per_word_p[p], self.avg_reply_time_p[p], self.median_reply_time_p[p]))
            
            # Emojis
            text_stats.append('')
            text_stats.append(f'Top {self.nbr_top_emojis} emojis: {list(self.top_emojis.keys())}')
            text_stats.append('')
            for i, p in enumerate(self.emojis_all_count, 1):
                if i > self.max_participants_on_plots:
                    break
                if self.emojis_all_count[p] == 0:
                    continue
                text_stats.append(f'{i}. {p}: {self.emojis_all_count[p]}')

            # Reactions emojis
            text_stats.append('')
            text_stats.append(f'Top {self.nbr_top_emojis} reactions emojis: {list(self.top_reactions_emojis.keys())}')
            text_stats.append('')
            for i, p in enumerate(self.emojis_reactions_all_count, 1):
                if i > self.max_participants_on_plots:
                    break
                if self.emojis_reactions_all_count[p] == 0:
                    continue
                text_stats.append(f'{i}. {p}: {self.emojis_reactions_all_count[p]}')


            y = 1.0
            for elem in text_stats:
                plt.text(0.0, y, elem, fontsize=12, verticalalignment='center')
                y -= 0.025

            pdf.savefig()
            plt.close()
            pb.printProgressBar()

            # Top words
            plt.title('Top words', fontsize=16, fontweight='bold')
            plt.axis('off')

            y = 0.95
            x = 0.0
            for j, word in enumerate(list(self.top_words.keys())[:self.nbr_top_words]):
                    plt.text(x, y - 0.025*(j+1), '{}. {}: {}'.format(j+1, list(self.top_words.keys())[j], list(self.top_words.values())[j]), fontsize=12, verticalalignment='center')
            for i, p in enumerate(list(self.nbr_msg_p.keys())[:4], 1):
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
            txt.write('Number of active days: {} ({:.3} %)\n'.format(self.nbr_days_active, 100*self.nbr_days_active/self.nbr_days))
            txt.write('Number of active days in row: {} ({} : {})\n'.format(self.nbr_days_active_in_row, self.time_start_days_active_in_row_str, self.time_end_days_active_in_row_str))
            txt.write('Number of inactive days in row: {} ({} : {})\n'.format(self.nbr_days_inactive_in_row, self.time_start_days_inactive_in_row_str, self.time_end_days_inactive_in_row_str))
            txt.write('Most messages in one day: {}\n'.format(max(self.nbr_times_day)))

            txt.write(banner('Messages') + '\n')
            txt.write('Number of messages: {}\n'.format(self.nbr_msg))
            txt.write(get_stats(self.nbr_msg_p, self.nbr_msg) + '\n')

            txt.write(banner('Words') + '\n')
            txt.write('Number of words: {}\n'.format(self.nbr_words))
            txt.write(get_stats(self.nbr_words_p, self.nbr_words) + '\n')
            
            txt.write(banner('Characters') + '\n')
            txt.write('Number of characters: {}\n'.format(self.nbr_chars))
            txt.write('Top {} characters: {}\n'.format(self.nbr_top_characters, list(self.top_chars.keys())[:self.nbr_top_characters]))
            txt.write(get_stats(self.nbr_chars_p, self.nbr_chars) + '\n')

            txt.write(banner('Averages') + '\n')
            txt.write('Average messages per day: {:.1f}\n'.format(self.avg_msg_per_day))
            txt.write('Average length of messages: {:.1f} words\n'.format(self.avg_words_per_msg))
            txt.write('Average length of messages: {:.1f} characters\n'.format(self.avg_chars_per_msg))
            txt.write('Average length of word: {:.1f} characters\n'.format(self.avg_chars_per_word))
            txt.write('Average reply time: {:.1f} seconds ({:.0f}h {:.0f}min) (rejecting >1day)'.format(self.avg_reply_time, self.avg_reply_time // 3600, (self.avg_reply_time % 3600) // 60))
            txt.write('Median reply time: {:.1f} seconds\n'.format(self.median_reply_time))
            txt.write('   {: <20} {: >12} {: >12} {: >15} {: >18} {: >18}\n'.format('Participant', 'Words/msg', 'Chars/msg', 'Chars/word', 'Avg reply time', 'Median reply time'))
            for i, p in enumerate(self.nbr_words_p, 1):
                txt.write('{}. {: <20}: {:>5.1f} w/msg{:>8.1f} ch/msg{:>7.1f} ch/w{:>11.0f} s{:>13.0f} s\n'.format(
                    i, p, self.avg_words_per_msg_p[p], self.avg_chars_per_msg_p[p], self.avg_chars_per_word_p[p], self.avg_reply_time_p[p], self.median_reply_time_p[p]))
            
            txt.write(banner('Edits') + '\n')
            txt.write('Number of editions: {}\n'.format(self.nbr_editions))
            #txt.write(get_stats(self.nbr_editions_p, self.nbr_editions) + '\n')

            txt.write(banner('Unsent messages') + '\n')
            txt.write('Number of unsent messages: {}\n'.format(self.nbr_unsent_msg))
            if self.nbr_unsent_msg: txt.write(get_stats(self.nbr_unsent_msg_p, self.nbr_unsent_msg) + '\n')

            txt.write(banner('Others') + '\n')
            txt.write('Number of photos: {}\n'.format(self.nbr_photos))
            if self.nbr_photos: txt.write(get_stats(self.nbr_photos_p, self.nbr_photos) + '\n')
            txt.write('Number of videos: {}\n'.format(self.nbr_videos))
            if self.nbr_videos: txt.write(get_stats(self.nbr_videos_p, self.nbr_videos) + '\n')
            txt.write('Number of gifs: {}\n'.format(self.nbr_gifs))
            if self.nbr_gifs: txt.write(get_stats(self.nbr_gifs_p, self.nbr_gifs) + '\n')
            txt.write('Number of stickers: {}\n'.format(self.nbr_stickers))
            if self.nbr_stickers: txt.write(get_stats(self.nbr_stickers_p, self.nbr_stickers) + '\n')
            txt.write('Number of files: {}\n'.format(self.nbr_files))
            if self.nbr_files: txt.write(get_stats(self.nbr_files_p, self.nbr_files) + '\n')
            txt.write('Number of audio: {}\n'.format(self.nbr_audio))
            if self.nbr_audio: txt.write(get_stats(self.nbr_audio_p, self.nbr_audio) + '\n')
            txt.write('Number of shares: {}\n'.format(self.nbr_shares))
            if self.nbr_shares: txt.write(get_stats(self.nbr_shares_p, self.nbr_shares) + '\n')

            # Emojis
            txt.write(banner('Emojis') + '\n')
            txt.write('Top {} emojis: {}\n'.format(self.nbr_top_emojis, list(self.top_emojis.keys())))
            txt.write(get_stats(self.emojis_all_count, sum(self.emojis_all_count.values())) + '\n')

            # Reactions emojis
            txt.write(banner('Reactions emojis') + '\n')
            txt.write('Top {} reactions emojis: {}\n'.format(self.nbr_top_emojis, list(self.top_reactions_emojis.keys())))
            txt.write(get_stats(self.emojis_reactions_all_count, sum(self.emojis_reactions_all_count.values())) + '\n')

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
    time_start = time.time()
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
    
    time_end = time.time()
    print('\nExecution time: {:.2f} seconds'.format(time_end - time_start))

    
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

def get_stats(nbr_p : dict, nbr_all : int, max_p : int = 10) -> str:
    """Creates a string with the top `max_p` participants from a dictionary.
    Args:
        nbr_p (dict): Dictionary with participants and their counts, must be sorted.
        nbr_all (int): Total number.
        max_p (int): Maximum number of participants to include.
    Returns:
        str: String with the top participants.
    """
    output = ''
    for i, p in enumerate(list(nbr_p.keys())[:max_p], 1):
        if nbr_p[p] == 0:
            break
        output += ('{}. {: <20}: {} ({:.1f}%)\n'.format(i, p, nbr_p[p], 100*nbr_p[p]/nbr_all))
    output = output[:-1]
    return output


def create_pie_chart(title : str, fracs : list, legend : list, pdf_file):
    # Set a wider range of colors for the color cycle
    if len(fracs) > 10:
        colors = plt.cm.tab20(np.linspace(0, 1, 20))
    else:
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
    plt.gca().set_prop_cycle('color', colors)
    plt.pie(fracs, startangle=90, autopct='%1.1f%%', pctdistance=0.75)
    plt.legend(legend,
            loc='upper left',
            bbox_to_anchor=(-0.15, 1.15))
    plt.axis('equal')
    plt.title(title)
    pdf_file.savefig()
    plt.close()

def create_pie_chart_with_rest(title : str, fracs, legend, max_on_plot : int, pdf_file, min_percentage : float = 2.5):
    # Add rest
    fracs = list(fracs)
    legend = list(legend)
    if len(fracs) > max_on_plot:
        min_val = sum(fracs) * min_percentage / 100
        for elem in fracs[:max_on_plot]:
            if elem < min_val:
                max_on_plot -= 1
        rest_val = sum(fracs) - sum(fracs[:max_on_plot])
        fracs = fracs[:max_on_plot]
        legend = legend[:max_on_plot]
        if rest_val != 0:
            fracs.append(rest_val)
            legend.append('Rest')
    create_pie_chart(title, fracs, legend, pdf_file)

if __name__ == '__main__':
    main()
