import logging
import os
import sqlite3
from datetime import datetime
import re
import codecs
import uuid
import json
import unicodedata


class SQLiteHandler(logging.Handler): # Inherit from logging.Handler
    """
    Logging handler that write logs to SQLite DB
    """
    def __init__(self, filename, channel_name):
        global db
        self.channel_name = channel_name
        self.stream_id = str(uuid.uuid4())
        self.botlist = ['moobot' 'nightbot', 'ohbot',
                        'deepbot', 'ankhbot', 'vivbot',
                        'wizebot', 'coebot', 'phantombot',
                        'xanbot', 'hnlbot', 'streamlabs',
                        'stay_hydrated_bot', 'botismo', 'streamelements',
                        'slanderbot', 'fossabot']
        
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        db = sqlite3.connect(filename) # might need to use self.filename
        
        
        create_query = '''CREATE TABLE IF NOT EXISTS 
                            chats_table(date datetime,
                               stream_date datetime,
                               stream_length INTEGER,
                               username text,
                               message_text text,
                               channel_name text,
                               stream_topic text,
                               stream_title text,
                               chatter_count INTEGER,
                               viewer_count INTEGER,
                               follower_count INTEGER,
                               subscriber_count INTEGER,
                               stream_id text)'''
        db.execute(create_query)
        db.commit()

    def emit(self, record, remove_bots = True):
         # Set up regex for hex decoding
        ESCAPE_SEQUENCE_RE = re.compile(r'''
            ( \\U........      # 8-digit hex escapes
            | \\u....          # 4-digit hex escapes
            | \\x..            # 2-digit hex escapes
            | \\[0-7]{1,3}     # Octal escapes
            | \\N\{[^}]+\}     # Unicode characters by name
            | \\[\\'"abfnrtv]  # Single-character escapes
            | \\r\\n
            )''', re.UNICODE | re.VERBOSE)
        
        
        def decode_escapes(s):
            def decode_match(match):
                return codecs.decode(match.group(0), 'unicode-escape')
            return ESCAPE_SEQUENCE_RE.sub(decode_match, s)
            
        def _split_line(line, firstLine = False):

            prefix = line[:28]        
            if firstLine:
                line = line.split('End of /NAMES list\\r\\n')[1]        
            splits = [message for ind, message in enumerate(line.split("\\r\\n")) 
                      if 'PRIVMSG' in message or ind == 0] 
            for i, case in enumerate(splits):
                if firstLine or i != 0:
                    splits[i] = prefix + splits[i]

            return splits
        # record.message is the log message
        thisdate = datetime.now()

         # Separate the raw strings into separate messages
        split_messages = []
        record_str = str(record.msg)
 
        split_log = record_str.split("||||")
    
        repaired_names = decode_escapes(split_log[1])
        user_log = json.loads(repaired_names)
        followers = decode_escapes(split_log[2])
        followers_log = json.loads(followers)
        line = split_log[0]
        chatter_count = int(split_log[3])
        viewer_count = int(split_log[4])
        stream_date = split_log[5]
        subs_count = int(split_log[6])
        stream_length = int(split_log[7][:-1])

        count = line.count('.tmi.twitch.tv PRIVMSG #')
        entryInfo = 'Your host is tmi.twitch.tv' in line or 'End of /NAMES list\\r\\n' in line
        if entryInfo:
            pass

        elif count == 0:
            pass
        elif count == 1 and not entryInfo:
            if line.endswith('\\r\\n\'\n') | line.endswith('\\r\\n\''):
                split_messages.append(line[:-6])
            else:
                split_messages.append(line)     
        else:
            for msg in _split_line(line):
                split_messages.append(msg)
        # Parse username, message text and (optional) datetime
        data = []          
        for message in split_messages:
            username = None
            message_text = None
            row = {}

            # Parse message text
            hash_channel_point = message.find("PRIVMSG #" + self.channel_name)
            slice_ = message[hash_channel_point:]

            slice_point = slice_.find(":") + 1
            message_text = slice_[slice_point:]
            try:
                decoded_txt = decode_escapes(message_text).encode('latin1').decode('utf-8')
            except:
                decoded_txt = "decoding failure"
            row['text'] = decoded_txt

            # Parse username
            b = message.find("b")
            exclam = message.find("!")
            username = message[b:exclam][3:]
            row['username'] = username

  
            # Store observations
            if remove_bots and row['username'] in self.botlist:
                pass
            else:
                data.append(row)
         
            insert_query = '''INSERT INTO chats_table(
                                          date, 
                                          stream_date,
                                          stream_length,
                                          username, 
                                          message_text, 
                                          channel_name,
                                          stream_topic,
                                          stream_title,
                                          chatter_count,
                                          viewer_count,
                                          follower_count,
                                          subscriber_count,
                                          stream_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''
            db.execute(insert_query,
            
            (
                thisdate,
                stream_date,
                stream_length,
                row['username'],
                row['text'],
                self.channel_name,
                user_log['data'][0]['game_name'],
                user_log['data'][0]['title'],
                chatter_count,
                viewer_count,
                followers_log['total'],
                subs_count,
                self.stream_id
            )
        )
            db.commit()


if __name__ == '__main__':
    # Create a logging object (after configuring logging)
    logger = logging.getLogger('someLoggerNameLikeDebugOrWhatever')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(SQLiteHandler('debugLog.sqlite'))
    logger.debug('Test 1')
    logger.warning('Some warning')
    logger.error('Alarma!')