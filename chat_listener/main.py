##5 * * * * /home/aspera/my_script.sh

from twitch_listener import utils
from twitch_listener import listener
import argparse
from load_sentiment_model import load_model
from transformers import BertTokenizer
import torch
import sqlite3


# Read in channels to listen to from arguments
parser = argparse.ArgumentParser(description='Get list of channels')
parser.add_argument('-l','--channels', nargs='+', help='<Required> set channels', required=True)

for _, value in parser.parse_args()._get_kwargs():
    if value is not None:
        channels_to_listen_to = value

# Define tokens        
nickname = 'twitch_pioneers'
oauth_chat = 'oauth:lolbsmiac5expvax1iqiysfo18hqi2'
client_id = '6resxnu2ehi2ggn0kgpue6g12bxtlw'
oauth_api = 'Bearer y5o8h4s2fljc1s632ylfrb540npcs0'

# Connect to chat server
bot = listener.connect_twitch(nickname, 
                             oauth_chat, 
                             client_id,
                             oauth_api)

# Returns list of live channels
channels_to_listen_to = utils.is_live(channels_to_listen_to)

# Get Broadcast ID for API calls
channels_to_listen_to = utils.get_broadcast_id(channels_to_listen_to, client_id, oauth_api)

# Scrape live chat data, viewers, followers, etc into sqlite database (Duration is seconds)
bot.listen(channels_to_listen_to, duration = 1000, until_offline = True, debug = False) 


# Score sentiment of chat messages
PRE_TRAINED_MODEL_NAME = "veb/twitch-bert-base-cased-pytorch" #'models/veb/twitch-bert-base-cased-finetuned'
MAX_LEN = 160
class_names = ['negative', 'neutral', 'positive']
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
model = load_model()
conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
cursor_obj = conn.cursor()

#Get messages with no sentiment
cursor_obj.execute("""select username, channel_name, date, message_text from chats_table_sentiment
                    where message_sentiment is NULL """)
output = cursor_obj.fetchall()

#Score each message and update table
for review_text in output:
    #Get sentiment for each message
    sentiment = utils.message_sentiment(review_text[3],
                                  tokenizer,
                                  model, 
                                  class_names, 
                                  PRE_TRAINED_MODEL_NAME,MAX_LEN = 160)
    #Update table with sentiments
    cursor_obj.execute("""UPDATE chats_table_sentiment
                        SET message_sentiment = {}
                        WHERE username = {} and 
                        channel_name = {} and
                        date = {};""".format(sentiment,
                                                "\'" + review_text[0] + "\'",
                                                 "\'" + review_text[1] + "\'",
                                                 "\'" + review_text[2] + "\'" ))

conn.commit()
conn.close()  
    