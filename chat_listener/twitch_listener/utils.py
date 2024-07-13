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
    """
    Set up file-based logging.

    Parameters:
        name (str): Name of the logger.
        log_file (str): File path for the log file.
        level (int): Logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger.
    """
    formatter = logging.Formatter('%(asctime)s — %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def setup_sqllite_loggers(channel_name, level=logging.INFO):
    """
    Set up SQLite-based logging for a given channel.

    Parameters:
        channel_name (str): Name of the channel.
        level (int): Logging level (default: logging.INFO).

    Returns:
        logging.Logger: Configured logger.
    """
    formatter = logging.Formatter('%(asctime)s — %(message)s')
    
    logger = logging.getLogger(channel_name)
    logger.setLevel(level)
    logger.addHandler(sqlite_handler.SQLiteHandler('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3', channel_name))

    return logger

def is_live(channel_list):
    """
    Check if specified channels are currently live.

    Parameters:
        channel_list (list): List of channel names.

    Returns:
        list: List of live channels.
    """
    live_channels = []
    for channel in channel_list:
        contents = requests.get('https://www.twitch.tv/' + channel).content.decode('utf-8')
        if 'isLiveBroadcast' in contents:
            live_channels.append(channel)
        
    return live_channels

def get_broadcast_id(channel_list, client_id, o_auth_api):
    """
    Get broadcast IDs for a list of channels.

    Parameters:
        channel_list (list): List of channel names.
        client_id (str): Twitch API client ID.
        o_auth_api (str): OAuth token for Twitch API.

    Returns:
        dict: Dictionary with channel names as keys and broadcast IDs as values.
    """
    id_list = {}
    for channel in channel_list:
        contents = requests.get('https://api.twitch.tv/helix/users?login=' + channel,
                                headers={"Authorization": o_auth_api, "Client-Id": client_id}).content.decode('utf-8')
        user_data = json.loads(contents)
        id_list[channel] = user_data['data'][0]['id']
        
    return id_list

def view_count(chatter_count):
    """
    Estimate viewer count based on chatter count.

    Parameters:
        chatter_count (int): Number of chatters.

    Returns:
        int: Estimated viewer count.
    """
    if chatter_count > 5000:
        viewer_count = round(chatter_count / 0.7)
    elif chatter_count <= 5000:
        viewer_count = round(chatter_count / 0.8)
    else:
        viewer_count = round(chatter_count / 0.8)
        
    # Adding some randomness to simulate real-world fluctuations
    viewer_count = random.randint(round(viewer_count * 0.95), round(viewer_count * 1.1))
                                    
    return viewer_count

def subscriber_count(followers):
    """
    Estimate subscriber count based on follower count.

    Parameters:
        followers (int): Number of followers.

    Returns:
        int: Estimated subscriber count.
    """
    if followers >= 10000:
        subscribers = round(followers / 80)
    elif followers >= 5000:
        subscribers = round(followers / 50)
    elif followers >= 200:
        subscribers = round(followers / 30)
    elif followers >= 100:
        subscribers = round(followers / 25)
    else:
        subscribers = round(followers / 25)
    
    # Adding some randomness to simulate real-world fluctuations
    subscribers = random.randint(round(subscribers * 0.95), round(subscribers * 1.1))
                                    
    return subscribers

def message_sentiment(review_text, tokenizer, model, class_names, PRE_TRAINED_MODEL_NAME, MAX_LEN=160):
    """
    Determine sentiment of a message using a BERT model.

    Parameters:
        review_text (str): Text of the review/message.
        tokenizer (BertTokenizer): Tokenizer for the BERT model.
        model (torch.nn.Module): Pre-trained BERT model.
        class_names (list): List of class names (e.g., ['negative', 'neutral', 'positive']).
        PRE_TRAINED_MODEL_NAME (str): Name of the pre-trained BERT model.
        MAX_LEN (int): Maximum length of the tokenized input (default: 160).

    Returns:
        str: Sentiment probability as a formatted string.
    """
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

    prob = torch.nn.functional.softmax(output, dim=1)
    top_prob = prob.topk(1, dim=1)[0].data[0].numpy()

    _, preds = torch.max(output, dim=1)

    pred_class = class_names[prediction]
    pred_proba = format(top_prob[0], '.6f') if pred_class == 'positive' else format(top_prob[0] * -1, '.6f') if pred_class == 'negative' else 0
    
    return pred_proba
