import logging
import requests
import json
from twitch_listener import sqlite_handler
import random

import torch
import sqlite3
from load_sentiment_model import load_model
from transformers import BertTokenizer

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
        logger.addHandler(sqlite_handler.SQLiteHandler('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3'
                                                       , channel_name))
        
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


def view_count(chatter_count):
    
    if chatter_count > 5000:
        viewer_count = round(chatter_count / .7)
    elif chatter_count <= 5000:
        viewer_count = round(chatter_count / .8)
    else:
        viewer_count = round(chatter_count / .8)
        
    viewer_count = random.randint(round(viewer_count *.95), round(viewer_count * 1.1))
                                    
        
    return viewer_count

def subscriber_count(followers):
    
    if followers >= 10000:
        subscribers = round(followers / 80)
    elif followers >= 5000:
        subscribers = round(followers / 50)
    elif followers >= 200:
        subscribers = round(followers / 30)
    elif followers >= 100:
        subscribers = round(followers / 25)
    elif followers >= 0:
        subscribers = round(followers / 25)
    else:
        subscribers = round(followers / 25)
    
    subscribers = random.randint(round(subscribers *.95), round(subscribers * 1.1))
                                    
        
    return subscribers


# import random
# import string
import sqlite3
import os

def message_sentiment(review_text, tokenizer, model, class_names, PRE_TRAINED_MODEL_NAME,MAX_LEN = 160):

    encoded_review = tokenizer.encode_plus(
    review_text,
    max_length=MAX_LEN,
    add_special_tokens=True,
    return_token_type_ids=False,
    pad_to_max_length=True,
    return_attention_mask=True,
    return_tensors='pt',
    )

    input_ids = encoded_review['input_ids']
    attention_mask = encoded_review['attention_mask']

    output = model(input_ids, attention_mask)
    _, prediction = torch.max(output, dim=1)
    # print(f'_____: {_}')


    prob = torch.nn.functional.softmax(output, dim=1)
    top_prob = prob.topk(1, dim=1)[0].data[0].numpy()

    _, preds = torch.max(output, dim=1)

    pred_class = class_names[prediction]
    pred_proba = format(top_prob[0], '.6f') if pred_class=='positive' else format(top_prob[0] * -1, '.6f') if pred_class=='negative' else 0
    
    return pred_proba

    
    