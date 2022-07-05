import logging
import os
import sqlite3
from datetime import datetime
import re

class SQLiteHandler(logging.Handler): # Inherit from logging.Handler
    """
    Logging handler that write logs to SQLite DB
    """
    def __init__(self, filename, channel_name):
        global db
        self.channel_name = channel_name
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Our custom argument
        db = sqlite3.connect(filename) # might need to use self.filename
        
#         create_query = '''CREATE TABLE IF NOT EXISTS 
#                             {}(date datetime,
#                                loggername text,
#                                filename,
#                                srclineno integer, 
#                                func text,
#                                level text,
#                                msg text)'''.format(self.channel_name)
        
        create_query = '''CREATE TABLE IF NOT EXISTS 
                            {}(date datetime,
                               username text,
                               message_text text,
                               channel_name text)'''.format(self.channel_name)
        db.execute(create_query)
        db.commit()

    def emit(self, record):
        
         # Set up regex for hex decoding
        ESCAPE_SEQUENCE_RE = re.compile(r'''
            ( \\U........      # 8-digit hex escapes
            | \\u....          # 4-digit hex escapes
            | \\x..            # 2-digit hex escapes
            | \\[0-7]{1,3}     # Octal escapes
            | \\N\{[^}]+\}     # Unicode characters by name
            | \\[\\'"abfnrtv]  # Single-character escapes
            )''', re.UNICODE | re.VERBOSE)
        
        def decode_escapes(s):
            def decode_match(match):
                return codecs.decode(match.group(0), 'unicode-escape')
            
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
#         thisdate = datetime.now()
        
#         #parse message
#         username = None
#         decoded_message = None
#         row = {}
        
#         # Parse message text
#         message_text = str(record.msg)
#         if '.tmi.twitch.tv PRIVMSG #' in message_text:
#             hash_channel_point = message_text.find("PRIVMSG #" + self.channel_name)
#             slice_ = message_text[hash_channel_point:]

#             slice_point = slice_.find(":") + 1
#             message_text = slice_[slice_point:]
#             try:
#                 decoded_message = decode_escapes(message_text).encode('latin1').decode('utf-8')
#             except:
#                 decoded_message = ''

#             # Parse username
#             b = message_text.find("b")
#             exclam = message_text.find("!")
#             username = message_text[b:exclam][3:]


 # Separate the raw strings into separate messages
        split_messages = []
        line = str(record.msg)
        count = line.count('.tmi.twitch.tv PRIVMSG #')
        entryInfo = 'Your host is tmi.twitch.tv' in line or 'End of /NAMES list\\r\\n' in line
        if entryInfo:
            pass

        elif count == 0:
            pass
        elif count == 1 and not entryInfo:
            if line.endswith('\\r\\n\'\n'):
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
            hash_channel_point = message.find("PRIVMSG #" + channel)
            slice_ = message[hash_channel_point:]

            slice_point = slice_.find(":") + 1
            message_text = slice_[slice_point:]
            decoded_txt = decode_escapes(message_text).encode('latin1').decode('utf-8')
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
         
        insert_query = '''INSERT INTO {}(
                                          date, 
                                          username, 
                                          message_text, 
                                          channel_name) VALUES(?,?,?,?)'''.format(self.channel_name)
        db.execute(insert_query,
            
            (
                'test',
                username,
                decoded_message,
                record.name
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