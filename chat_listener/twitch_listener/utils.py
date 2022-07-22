import logging
import requests
import json
from twitch_listener import sqlite_handler

def setup_loggers(name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s — %(message)s')
        handler = logging.FileHandler(log_file)        
        handler.setFormatter(formatter)
    
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger

def setup_sqllite_loggers(channel_name, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s — %(message)s')
        #handler = logging.FileHandler(sqlite_handler.SQLiteHandler('db.sqlite3'))        
        #handler.setFormatter(formatter)
    
        logger = logging.getLogger(channel_name)
        logger.setLevel(level)
        logger.addHandler(sqlite_handler.SQLiteHandler('db.sqlite3', channel_name))
        
#         logger = logging.getLogger('someLoggerNameLikeDebugOrWhatever')
#         logger.setLevel(logging.DEBUG)
#         logger.addHandler(SQLiteHandler('db.sqlite3'))
#         logger.debug('Test 1')
#         logger.warning('Some warning')
#         logger.error('Alarma!')

        return logger
    
def is_live(channel_list):
    
    live_channels = []
    for channel in channel_list:
        contents = requests.get('https://www.twitch.tv/' +channel).content.decode('utf-8')

        if 'isLiveBroadcast' in contents:
            live_channels.append(channel)
        
    return live_channels

def get_broadcast_id(channel_list, client_id, o_auth_api):
    
    id_list = {}
    for channel in channel_list:
        contents = requests.get('https://api.twitch.tv/helix/users?login=' + channel,
                        headers={"Authorization":o_auth_api, "Client-Id": client_id}).content.decode('utf-8')
        user_data = json.loads(contents)
        id_list[channel] = user_data['data'][0]['id']  
        
    return id_list