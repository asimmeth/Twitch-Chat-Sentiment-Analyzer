##5 * * * * /home/aspera/my_script.sh

from twitch_listener import utils
from twitch_listener import listener
import argparse


#Import channels to listen to
parser = argparse.ArgumentParser(description='Get list of channels')
parser.add_argument('-l','--channels', nargs='+', help='<Required> set channels', required=True)


for _, value in parser.parse_args()._get_kwargs():
    if value is not None:
        channels_to_listen_to = value
# Connect to Twitch
bot = listener.connect_twitch('twitch_pioneers', 
                             'oauth:zkekfhyhzhdl8ltxs6b8jdez7b2i6b', 
                             'capstone_pioneers')


#returns list of live channels
live_channels = utils.is_live(channels_to_listen_to)

#If no channels
if len(live_channels) == 0:
    print("No Channels Live")
else:
    bot.listen(channels_to_listen_to, until_offline = True) 
