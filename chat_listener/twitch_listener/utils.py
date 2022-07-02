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

def setup_sqllite_loggers(name, log_file, level=logging.INFO):
        formatter = logging.Formatter('%(asctime)s — %(message)s')
        handler = logging.FileHandler(SQLiteHandler('debug_log.sqlite'))        
        handler.setFormatter(formatter)
    
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)

        return logger
    
def is_live(channel_list):
    
    for channel in channel_list:
        contents = requests.get('https://www.twitch.tv/' +channel).content.decode('utf-8')

        if 'isLiveBroadcast' not in contents:
            channel_list.remove(channel)
        
    return channel_list