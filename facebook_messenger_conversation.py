import sys
import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import emoji


class FacebookMessengerConversation():
    """Module for getting stats of a Facebook Messenger conversation.

    Attributes:
        data (dict): The conversation of interest.
        title (str) : Title of the conversation.
        p (list): List of conversation participants.

    """

    def __init__(self, conversation):
        """Prepares `conversation` and fetches its participants.

        Args:
            conversation (json): Conversation downloaded from
                Facebook (see https://www.facebook.com/help/
                212802592074644?helpref=uf_permalink)

        """
        self.data = json.load(open(conversation))
        self.title = self.data['title']

        # Convert unicode characters
        for p in self.data['participants']:
            p['name'] = p['name'].encode('raw_unicode_escape').decode('utf-8')
        for message in self.data['messages']:
            message['sender_name'] = message['sender_name'].encode(
                'raw_unicode_escape').decode('utf-8')
            if 'content' in message:
                message['content'] = message['content'].encode(
                    'raw_unicode_escape').decode('utf-8')

        # Set names of conversation participants
        #nbr_participants = len(self.data['participants'])
        #self.p = nbr_participants * [None]
        #for i in range(nbr_participants):
        #    self.p[i] = self.data['participants'][i]['name']

        # For group chats where the participants left the chat
        nbr_participants = 0
        self.p = []
        for message in self.data['messages']:
            if 'sender_name' in message:
                if message['sender_name'] not in self.p and len(message['sender_name']) > 0:
                    self.p.append(message['sender_name'])
                    nbr_participants += 1

    def get_participants(self):
        """Returns the names of the conversation participants.

        Returns:
            list: Contains the conversation participants

        """
        return self.p

    def get_time_interval(self, type):
        """Returns the start and end time of the conversation.

        Args:
            type (str): Decides what type should be returned. Either
                'datetime' or 'str'.

        Returns:
            tuple: (start, end). Either as datetimes or strings.

        Raises:
            ValueError: If a not supported `type` was entered.

        """
        start = datetime.fromtimestamp(
            self.data['messages'][-1]['timestamp_ms']/1000)
        end = datetime.fromtimestamp(
            self.data['messages'][0]['timestamp_ms']/1000)
        if type == 'datetime':
            return start, end
        elif type == 'str':
            return start.strftime('%Y-%m-%d %H:%M:%S'), \
                end.strftime('%Y-%m-%d %H:%M:%S')
        else:
            raise ValueError('Type not supported. Must be '\
                             'either datetime or str.')

    def get_nbr_days(self):
        """Returns the number days between the first and last message.

        Returns:
            int: Days between start and end.

        """
        start, end = self.get_time_interval('datetime')
        return (end - start).days + 1

    def get_nbr_days_active(self):
        """Returns the number of days messages were sent.

        Returns:
            int: Number of days messages were sent.

        """
        days = set()
        for message in self.data['messages']:
            current = datetime.fromtimestamp(
                message['timestamp_ms']/1000).date()
            days.add(current)
        return len(days)

    def get_nbr_msg(self):
        """Returns the total number of messages.

        Returns:
            int: Number of messages.

        """
        return len(self.data['messages'])

    def get_nbr_words(self):
        """Returns the total number of words.

        Returns:
            int: Number of words.

        """
        nbr_words = 0
        for message in self.data['messages']:
            if 'content' in message:
                nbr_words += len(message['content'].split())
        return nbr_words
    
    def get_nbr_words_p(self):
        """Returns the total number of words per participant.

        Returns:
            dict: Contains the number of words per participant.

        """
        nbr_words_p = {p: 0 for p in self.p}
        for message in self.data['messages']:
            if 'content' in message:
                try:
                    sender = message['sender_name']
                    nbr_words_p[sender] += len(message['content'].split())
                except KeyError:
                    pass
        nbr_words_p = {p: nbr_words_p[p] if nbr_words_p[p] > 0 else 1 for p in nbr_words_p}
        nbr_words_p_sorted = dict(sorted(nbr_words_p.items(), key=lambda item: item[1], reverse=True))
        return nbr_words_p_sorted

    def get_nbr_characters_p(self):
        """Returns the total number of characters per participant.

        Returns:
            dict: Contains the number of characters per participant.

        """
        nbr_characters_p = {p: 0 for p in self.p}
        for message in self.data['messages']:
            if 'content' in message:
                try:
                    sender = message['sender_name']
                    nbr_characters_p[sender] += len(message['content'])
                except KeyError:
                    pass
        nbr_characters_p_sorted = dict(sorted(nbr_characters_p.items(), key=lambda item: item[1], reverse=True))
        return nbr_characters_p_sorted

    def get_avg_len_msg(self):
        """Returns the average length of a message in words.

        Returns:
            float: Average length of message in words.

        """
        return round(self.get_nbr_words()/self.get_nbr_msg(), 1)

    def get_avg_msg_day(self):
        """Returns the average number of messages sent each day.

        Returns:
            float: Average number of messages sent per day.

        """
        return round(self.get_nbr_msg()/self.get_nbr_days(), 1)

    def activity(self):
        """Activity by each conversation participant.

        Returns:
            dict: Contains a list (value) with the number of messages
                sent and the percentage it corresponds to per
                participant (key).

        """
        nbr_msg = self.get_nbr_msg()
        act = {p: 0 for p in self.p}
        for message in self.data['messages']:
            try:
                act[message['sender_name']] += 1
            except KeyError:
                pass
        
        # Sort the dictionary by the number of messages sent (nbr_msg_p) in descending order
        act_sorted = dict(sorted(act.items(), key=lambda item: item[1], reverse=True))

        for key in act_sorted:
            nbr_msg_p = act_sorted[key]
            act_sorted[key] = [nbr_msg_p, 100*nbr_msg_p/nbr_msg]
        return act_sorted

    def timeline(self):
        """Fetches data when messages are sent.

        Returns:
            tuple: Containing which days messages were sent and also
                how many were sent per day, weekday and hour.

        """
        nbr_days = self.get_nbr_days()
        timeline = [None] * nbr_days
        hour = list(range(24))
        weekday_arr = [0, 1, 2, 3, 4, 5, 6]
        nbr_times_hour = [0] * 24
        nbr_times_weekday = [0] * 7
        nbr_times_day = [0] * nbr_days
        _, end = self.get_time_interval('datetime')
        current_day = end.date()
        index = len(timeline) - 1
        timeline[index] = current_day
        nbr_times_day[index] = 1
        for message in self.data['messages']:
            current = datetime.fromtimestamp(
                message['timestamp_ms']/1000)
            h = int(round(current.hour + current.minute/60. +\
                current.second/3600))
            if h == 24:
                h = 0
            nbr_times_hour[h] = nbr_times_hour[h] + 1
            wd = current.weekday()
            nbr_times_weekday[wd] = nbr_times_weekday[wd] + 1
            current = current.date()
            if current == current_day:
                nbr_times_day[index] = nbr_times_day[index] + 1
            elif current < current_day:
                diff = (current_day - current).days
                index = index - diff
                current_day = current
                timeline[index] = current_day
                nbr_times_day[index] = 1
        dates = [None] * len(timeline)
        for i in range(0, len(timeline)):
            if timeline[i] == None:
                timeline[i] = timeline[i - 1] + timedelta(days=1)
            dates[i] = timeline[i].strftime('%Y-%m-%d')
        return timeline, nbr_times_day, nbr_times_weekday, nbr_times_hour

    def top_emojis(self, nbr):
        """Returns the top `nbr` emojis used and who sent them.

        Args:
            nbr (int): The number of emojis to include in top list.

        Returns:
            tuple:  List of top emojis
                    Dict showing how many of these were sent by each participant
                    Dict showing number of all emojis sent by each participant

        """
        all_emojis_count = {p: 0 for p in self.p}
        emojis = {e: 0 for e in iter(emoji.UNICODE_EMOJI.values())}
        emojis_p = {p: 0 for p in self.p}
        for p in emojis_p:
            emojis_p[p] = {e: 0 for e in iter(emoji.UNICODE_EMOJI.values())}
        for message in self.data['messages']:
            if 'content' in message:
                try:
                    msg = message['content']
                    sender = message['sender_name']
                    for c in msg:
                        emoji_str = emoji.demojize(c)
                        if emoji_str in emojis and sender in emojis_p:
                            emojis_p[sender][emoji_str] += 1
                            emojis[emoji_str] += 1
                            all_emojis_count[sender] += 1
                except KeyError:
                    pass
                
        top_emojis = [emoji_key for emoji_key, count in sorted(emojis.items(),
                                       key=lambda kv: (-kv[1], kv[0]))[:nbr]]
        emojis_count_p = {p: {} for p in self.p}
        for p in self.p:
                emojis_count_p[p] = [emojis_p[p][e] for e in top_emojis]
        top_emojis = [emoji.emojize(top_emoji) for top_emoji in top_emojis]

        all_emojis_count_sorted = dict(sorted(all_emojis_count.items(), key=lambda item: item[1], reverse=True))

        return top_emojis, emojis_count_p, all_emojis_count_sorted

    def top_reactions_emojis(self, nbr):
        """Returns the top `nbr` emojis used in reactions and who sent them.

        Args:
            nbr (int): The number of emojis to include in top list.

        Returns:
            tuple:  List of top reactions emojis
                    Dict showing how many of these were sent by each participant
                    Dict showing number of all emojis sent by each participant


        """
        all_emojis_count = {p: 0 for p in self.p}
        emojis = {e: 0 for e in iter(emoji.UNICODE_EMOJI.values())}
        emojis_p = {p: 0 for p in self.p}
        for p in emojis_p:
            emojis_p[p] = {e: 0 for e in iter(emoji.UNICODE_EMOJI.values())}
        for message in self.data['messages']:
            if 'reactions' in message:
                for reaction in message['reactions']:
                    try:
                        actor = reaction['actor']
                        emoji_str = emoji.demojize(reaction['reaction'].encode("raw_unicode_escape").decode("utf-8"))
                        if emoji_str in emojis and actor in emojis_p:
                            emojis_p[actor][emoji_str] += 1
                            emojis[emoji_str] += 1
                            all_emojis_count[actor] += 1
                    except KeyError:
                        pass
                    

        top_emojis = [emoji_key for emoji_key, count in sorted(emojis.items(),
                                       key=lambda kv: (-kv[1], kv[0]))[:nbr]]
        emojis_count_p = {p: {} for p in self.p}
        for p in self.p:
                emojis_count_p[p] = [emojis_p[p][e] for e in top_emojis]
        top_emojis = [emoji.emojize(top_emoji) for top_emoji in top_emojis]

        all_emojis_count_sorted = dict(sorted(all_emojis_count.items(), key=lambda item: item[1], reverse=True))

        return top_emojis, emojis_count_p, all_emojis_count_sorted
    
    def top_characters(self, nbr):
        """Returns the top `nbr` characters used without spaces

        Args:
            nbr (int): The number of characters to include in top list.

        Returns:
            Dict showing the top characters used with their counts

        """
        characters = {c: 0 for c in set(''.join([message['content'].lower() for message in self.data['messages'] if 'content' in message]))}
        for message in self.data['messages']:
            if 'content' in message:
                msg = message['content'].lower()
                for c in msg:
                    if c != ' ':
                        characters[c] += 1
        top_characters = {character_key: count for character_key, count in sorted(characters.items(),
                           key=lambda kv: (-kv[1], kv[0]))[:nbr]}
        return top_characters
    
    def top_words(self, nbr):
        """Returns the top `nbr` words used

        Args:
            nbr (int): The number of words to include in top list.

        Returns:
            Dict showing the top words used with their counts

        """
        words = {}
        for message in self.data['messages']:
            if 'content' in message:
                msg = message['content']
                for word in msg.split():
                    if word in words:
                        words[word] += 1
                    else:
                        words[word] = 1
        top_words = {word_key: count for word_key, count in sorted(words.items(),
                           key=lambda kv: (-kv[1], kv[0]))[:nbr]}
        return top_words
    
    def top_words_p(self, nbr):
        """Returns the top `nbr` words used per participant

        Args:
            nbr (int): The number of words to include in top list.

        Returns:
            Dict showing the top words used with their counts per participant

        """
        words_p = {p: {} for p in self.p}
        for p in self.p:
            words_p[p] = {}
        for message in self.data['messages']:
            if 'content' in message:
                try:
                    msg = message['content']
                    sender = message['sender_name']
                    for word in msg.split():
                        if word in words_p[sender]:
                            words_p[sender][word] += 1
                        else:
                            words_p[sender][word] = 1
                except KeyError:
                    pass
                
        top_words_p = {p: {word_key: count for word_key, count in sorted(words_p[p].items(),
                           key=lambda kv: (-kv[1], kv[0]))[:nbr]} for p in self.p}
        return top_words_p