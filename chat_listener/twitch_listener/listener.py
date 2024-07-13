import pandas as pd
from socket import socket
from time import time, sleep
from twitch_listener import utils
import select
import re
import codecs
from pathlib import Path
import os
from twitch_listener import utils
import requests
import json
from datetime import datetime
import urllib.request, json 
from datetime import date

class connect_twitch(socket):
    
    def __init__(self, nickname, oauth, client_id, oauth_api):
        """
        Initialize the Twitch connection class with user credentials and setup IRC parameters.
        
        Parameters:
            nickname (str): Twitch username.
            oauth (str): OAuth token for IRC authentication.
            client_id (str): Client ID for Twitch API.
            oauth_api (str): OAuth token for Twitch API.
        """
        self.nickname = nickname
        self.client_id = client_id

        # Ensure the OAuth token is correctly formatted
        if oauth.startswith('oauth:'):
            self.oauth = oauth
        else:
            self.oauth = 'oauth:' + oauth
        
        if oauth_api.startswith('Bearer'):
            self.oauth_api = oauth_api
        else:
            self.oauth_api = 'Bearer ' + oauth_api

        # List of common bot usernames to filter out
        self.botlist = ['moobot', 'nightbot', 'ohbot', 'deepbot', 'ankhbot', 'vivbot', 'wizebot', 
                        'coebot', 'phantombot', 'xanbot', 'hnlbot', 'streamlabs', 'stay_hydrated_bot', 
                        'botismo', 'streamelements', 'slanderbot', 'fossabot']
            
        # IRC server parameters
        self._server = "irc.chat.twitch.tv"
        self._port = 6667
        self._passString = f"PASS " + self.oauth + f"\n"
        self._nameString = f"NICK " + self.nickname + f"\n"
        
        # Separator for logged data
        self.bytes_seperator = bytes("||||", 'utf-8')
        

    def _join_channels(self, channels):
        """
        Join specified Twitch channels by establishing socket connections.
        
        Parameters:
            channels (dict): Dictionary of channels and their broadcast IDs.
        """
        self._sockets = {}
        self.joined = {}
        self._loggers = {}
        
        # Establish socket connections for each channel
        for channel, broadcast_id in channels.items():
            self._sockets[channel] = socket()
            self._sockets[channel].connect((self._server, self._port))
            self._sockets[channel].send(self._passString.encode('utf-8'))
            self._sockets[channel].send(self._nameString.encode('utf-8'))
            
            joinString = f"JOIN #" + channel.lower() + f"\n"
            self._sockets[channel].send(joinString.encode('utf-8'))
            
            # Setup loggers for each channel
            self._loggers[channel] = utils.setup_sqllite_loggers(channel)
            self.joined[channel] = broadcast_id
        
    def listen(self, channels, duration=1000, until_offline=False, debug=False, file_path=''):
        """
        Method for scraping chat data from Twitch channels.

        Parameters:
            channels (dict): Dictionary of channels and their broadcast IDs.
            duration (int): Length of time to listen for (in seconds).
            until_offline (bool): Listen until the channels go offline if set to True.
            debug (bool): If True, prints debug information.
            file_path (str): File path for logging (not used in the current implementation).
        """
        self._join_channels(channels)  # Join the specified channels
        startTime = time()
        start_time = datetime.now()
        start_date = date.today()
        
        if until_offline is False:
            # Collect data while duration not exceeded and channels are live
            while (time() - startTime) < duration: 
                # Check if channels are live
                if len(utils.is_live(channels)) == 0:
                    print("Channels Offline")
                    break

                now = time()  # Track loop time for adaptive rate limiting
                ready_socks, _, _ = select.select(self._sockets.values(), [], [], 1)
                for channel, broadcast_id in self.joined.items():
                    sock = self._sockets[channel]
                    if sock in ready_socks:
                        response = sock.recv(16384)
                        # Respond to PING messages from Twitch
                        if b"PING :tmi.twitch.tv\r\n" in response:
                            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                            if debug:
                                print("\n\n!!Look, a ping: \n")
                                print(response)
                                print("\n\n")
                        else:
                            # Fetch additional metadata from Twitch API
                            contents_name = requests.get(
                                'https://api.twitch.tv/helix/channels?broadcaster_id=' + broadcast_id,
                                headers={"Authorization": self.oauth_api, "Client-Id": self.client_id}
                            ).content

                            followers = requests.get(
                                'https://api.twitch.tv/helix/users/follows?to_id=' + broadcast_id,
                                headers={"Authorization": self.oauth_api, "Client-Id": self.client_id}
                            ).content
                            
                            followers_count = json.loads(followers)['total']
                            stream_length = datetime.now() - start_time
                            td_mins = int(round(stream_length.total_seconds() / 60))
                            
                            with urllib.request.urlopen(f'https://tmi.twitch.tv/group/user/{channel}/chatters') as url:
                                chatter_count = json.loads(url.read().decode())['chatter_count']
                                
                            viewer_count = utils.view_count(chatter_count)
                            subs_count = utils.subscriber_count(followers_count)
                                  
                            # Log the collected data
                            self._loggers[channel].info(
                                response + self.bytes_seperator 
                                + contents_name + self.bytes_seperator 
                                + followers + self.bytes_seperator
                                + bytes(str(chatter_count), 'utf-8') + self.bytes_seperator
                                + bytes(str(viewer_count), 'utf-8') + self.bytes_seperator 
                                + bytes(str(start_time), 'utf-8') + self.bytes_seperator
                                + bytes(str(subs_count), 'utf-8') + self.bytes_seperator
                                + bytes(str(start_date), 'utf-8') + self.bytes_seperator
                                + bytes(str(td_mins), 'utf-8')
                            )

                            if debug:
                                print(response)
                        elapsed = time() - now
                        # Implement rate limiting
                        if elapsed < 60 / 800:
                            sleep((60 / 800) - elapsed)
                    else:
                        pass
                
        else:
            online = True
            while online: 
                # Check if channels are live
                if len(utils.is_live(channels)) == 0:
                    online = False
                    print("Channels Offline")
                    break

                now = time()  # Track loop time for adaptive rate limiting
                ready_socks, _, _ = select.select(self._sockets.values(), [], [], 1)
                for channel, broadcast_id in self.joined.items():
                    sock = self._sockets[channel]
                    if sock in ready_socks:
                        response = sock.recv(16384)
                        # Respond to PING messages from Twitch
                        if b"PING :tmi.twitch.tv\r\n" in response:
                            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                            if debug:
                                print("\n\n!!Look, a ping: \n")
                                print(response)
                                print("\n\n")
                        else:
                            # Fetch additional metadata from Twitch API
                            contents_name = requests.get(
                                'https://api.twitch.tv/helix/channels?broadcaster_id=' + broadcast_id,
                                headers={"Authorization": self.oauth_api, "Client-Id": self.client_id}
                            ).content
                            
                            followers = requests.get(
                                'https://api.twitch.tv/helix/users/follows?to_id=' + broadcast_id,
                                headers={"Authorization": self.oauth_api, "Client-Id": self.client_id}
                            ).content
                            
                            followers_count = json.loads(followers)['total']
                            stream_length = datetime.now() - start_time
                            td_mins = int(round(stream_length.total_seconds() / 60))
                                  
                            with urllib.request.urlopen(f'https://tmi.twitch.tv/group/user/{channel}/chatters') as url:
                                chatter_count = json.loads(url.read().decode())['chatter_count']
                                
                            viewer_count = utils.view_count(chatter_count)
                            subs_count = utils.subscriber_count(followers_count)
                                  
                            # Log the collected data
                            self._loggers[channel].info(
                                response + self.bytes_seperator 
                                + contents_name + self.bytes_seperator 
                                + followers + self.bytes_seperator
                                + bytes(str(chatter_count), 'utf-8') + self.bytes_seperator
                                + bytes(str(viewer_count), 'utf-8') + self.bytes_seperator 
                                + bytes(str(start_time), 'utf-8') + self.bytes_seperator
                                + bytes(str(subs_count), 'utf-8') + self.bytes_seperator
                                + bytes(str(start_date), 'utf-8') + self.bytes_seperator
                                + bytes(str(td_mins), 'utf-8')
                            )

                            if debug:
                                print(response)
                        elapsed = time() - now
                        # Implement rate limiting
                        if elapsed < 60 / 800:
                            sleep((60 / 800) - elapsed)
                    else:
                        pass
        if debug:
            print("Collected for " + str(time() - startTime) + " seconds")
        
        # Close sockets once not collecting data
        for channel in self.joined:
            self._sockets[channel].close()