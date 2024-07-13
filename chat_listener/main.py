##5 * * * * /home/aspera/my_script.sh

from twitch_listener import utils
from twitch_listener import listener
import argparse
from load_sentiment_model import load_model
from transformers import BertTokenizer
import torch
import sqlite3

# Parse command-line arguments to get the list of channels to listen to
parser = argparse.ArgumentParser(description='Get list of channels')
parser.add_argument('-l', '--channels', nargs='+', help='<Required> set channels', required=True)

for _, value in parser.parse_args()._get_kwargs():
    if value is not None:
        channels_to_listen_to = value

# Define authentication tokens and credentials for Twitch API
nickname = 'twitch_pioneers'
oauth_chat = 'oauth:lolbsmiac5expvax1iqiysfo18hqi2'
client_id = '6resxnu2ehi2ggn0kgpue6g12bxtlw'
oauth_api = 'Bearer y5o8h4s2fljc1s632ylfrb540npcs0'

# Initialize the Twitch listener bot with the provided credentials
bot = listener.connect_twitch(nickname, 
                             oauth_chat, 
                             client_id,
                             oauth_api)

# Get the list of live channels from the provided list
channels_to_listen_to = utils.is_live(channels_to_listen_to)

# Get broadcast IDs for the live channels to make API calls
channels_to_listen_to = utils.get_broadcast_id(channels_to_listen_to, client_id, oauth_api)

# Start listening to the live chat data from the specified channels
# and store the data in an SQLite database (Duration is in seconds)
bot.listen(channels_to_listen_to, duration=1000, until_offline=True, debug=False) 

# Set up for sentiment analysis of chat messages
PRE_TRAINED_MODEL_NAME = "veb/twitch-bert-base-cased-pytorch"
MAX_LEN = 160
class_names = ['negative', 'neutral', 'positive']
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
model = load_model()

# Connect to the SQLite database
conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
cursor_obj = conn.cursor()

# Get messages from the database that do not have a sentiment score
cursor_obj.execute("""SELECT username, channel_name, date, message_text FROM chats_table_sentiment
                    WHERE message_sentiment IS NULL""")
output = cursor_obj.fetchall()

# Score the sentiment of each message and update the database
for review_text in output:
    # Get sentiment score for each message
    sentiment = utils.message_sentiment(review_text[3],
                                        tokenizer,
                                        model, 
                                        class_names, 
                                        PRE_TRAINED_MODEL_NAME, MAX_LEN=160)
    # Update the database with the sentiment scores
    cursor_obj.execute("""UPDATE chats_table_sentiment
                          SET message_sentiment = {}
                          WHERE username = {} AND 
                          channel_name = {} AND
                          date = {};""".format(sentiment,
                                               "\'" + review_text[0] + "\'",
                                               "\'" + review_text[1] + "\'",
                                               "\'" + review_text[2] + "\'"))

# Commit the changes to the database and close the connection
conn.commit()
conn.close()
