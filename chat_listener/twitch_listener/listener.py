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

class connect_twitch(socket):
    
    def __init__(self, nickname, oauth, client_id, oauth_api):

        self.nickname = nickname
        
        self.client_id = client_id
        if oauth.startswith('oauth:'):
            self.oauth = oauth
        else:
            self.oauth = 'oauth:' + oauth
        
        if oauth_api.startswith('Bearer'):
            self.oauth_api = oauth_api
        else:
            self.oauth_api = 'Bearer ' + oauth_api
        self.botlist = ['moobot' 'nightbot', 'ohbot',
                        'deepbot', 'ankhbot', 'vivbot',
                        'wizebot', 'coebot', 'phantombot',
                        'xanbot', 'hnlbot', 'streamlabs',
                        'stay_hydrated_bot', 'botismo', 'streamelements',
                        'slanderbot', 'fossabot']
            
        # IRC parameters
        self._server = "irc.chat.twitch.tv"
        self._port = 6667
        self._passString = f"PASS " + self.oauth + f"\n"
        self._nameString = f"NICK " + self.nickname + f"\n"
        
        self.bytes_seperator = bytes("||||", 'utf-8')
        

        
        
        

    def _join_channels(self, channels):

        self._sockets = {}
        self.joined = {}
        self._loggers = {}
        
        # Establish socket connections
        for channel, broadcast_id in channels.items():
            self._sockets[channel] = socket()
            self._sockets[channel].connect((self._server, self._port))
            self._sockets[channel].send(self._passString.encode('utf-8'))
            self._sockets[channel].send(self._nameString.encode('utf-8'))
            
            joinString = f"JOIN #" + channel.lower() + f"\n"
            self._sockets[channel].send(joinString.encode('utf-8'))
            #self._loggers[channel] = utils.setup_loggers(channel, os.getcwd() + '/logs/' + channel + '.log')
            self._loggers[channel] = utils.setup_sqllite_loggers(channel)
            
            self.joined[channel] = broadcast_id
        
    def listen(self, channels, duration = 1000, until_offline = False, debug = False, file_path = ''):

        """
        Method for scraping chat data from Twitch channels.

        Parameters:
            channels (string or list) 
                - Channel(s) to connect to.
            duration (int)           
                 - Length of time to listen for.
            debug (bool, optional)             
                 - Debugging feature, will likely be removed in later version.
        """

        
        self._join_channels(channels)
        startTime = time()
        start_time = datetime.now()
        
        if until_offline is False:
            # Collect data while duration not exceeded and channels are live
            while (time() - startTime) < duration: 

                if len(utils.is_live(channels)) == 0:
                    print("Channels Offline")
                    break

                now = time() # Track loop time for adaptive rate limiting
                ready_socks,_,_ = select.select(self._sockets.values(), [], [], 1)
                for channel, broadcast_id in self.joined.items():
                    sock = self._sockets[channel]
                    if sock in ready_socks:
                        response = sock.recv(16384)
                        if b"PING :tmi.twitch.tv\r\n" in response:
                            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                            if debug:
                                print("\n\n!!Look, a ping: \n")
                                print(response)
                                print("\n\n")
                        else:
                            contents_name = requests.get('https://api.twitch.tv/helix/channels?broadcaster_id=' + broadcast_id,
                                headers={"Authorization":self.oauth_api,
                                         "Client-Id": self.client_id}).content

                            followers = requests.get('https://api.twitch.tv/helix/users/follows?to_id=' + broadcast_id,
                                headers={"Authorization":self.oauth_api,
                                         "Client-Id": self.client_id}).content
                            stream_length = datetime.now() - start_time
                            td_mins = int(round(stream_length.total_seconds() / 60))
                            
                            with urllib.request.urlopen('https://tmi.twitch.tv/group/user/{}/chatters'.format(channel)) as url:
                                chatter_count = json.loads(url.read().decode())['chatter_count']
                                
                            if chatter_count > 5000:
                                viewer_count = round(chatter_count / .7)
                            elif chatter_count < 5000:
                                viewer_count = round(chatter_count / .8)
                            else:
                                viewer_count = round(chatter_count / .8)
                                  
                            self._loggers[channel].info(response + self.bytes_seperator 
                                                + contents_name + self.bytes_seperator 
                                                + followers + self.bytes_seperator
                                                + bytes(str(chatter_count),'utf-8') + self.bytes_seperator
                                                + bytes(str(viewer_count),'utf-8') + self.bytes_seperator 
                                                + bytes(str(start_time),'utf-8') + self.bytes_seperator       
                                                + bytes(str(td_mins), 'utf-8')) 

                            if debug:
                                print(response)
                        elapsed = time() - now
                        if elapsed < 60/800:
                            sleep( (60/800) - elapsed) # Rate limit
                    else: # if not in ready_socks
                        pass
                
        else:
            online = True
            while online: 

                if len(utils.is_live(channels)) == 0:
                    online = False
                    print("Channels Offline")
                    break

                now = time() # Track loop time for adaptive rate limiting
                ready_socks,_,_ = select.select(self._sockets.values(), [], [], 1)
                for channel, broadcast_id in self.joined.items():
                    sock = self._sockets[channel]
                    if sock in ready_socks:
                        response = sock.recv(16384)
                        if b"PING :tmi.twitch.tv\r\n" in response:
                            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
                            if debug:
                                print("\n\n!!Look, a ping: \n")
                                print(response)
                                print("\n\n")
                        else:
                            contents_name = requests.get('https://api.twitch.tv/helix/channels?broadcaster_id=' + broadcast_id,
                                        headers={"Authorization":self.oauth_api,
                                                 "Client-Id": self.client_id}).content
                            
                            followers = requests.get('https://api.twitch.tv/helix/users/follows?to_id=' + broadcast_id,
                                        headers={"Authorization":self.oauth_api,
                                                 "Client-Id": self.client_id}).content

                            stream_length = datetime.now() - start_time
                            td_mins = int(round(stream_length.total_seconds() / 60))
                                  
                            with urllib.request.urlopen('https://tmi.twitch.tv/group/user/{}/chatters'.format(channel)) as url:
                                chatter_count = json.loads(url.read().decode())['chatter_count']
                                
                            if chatter_count > 5000:
                                viewer_count = round(chatter_count / .7)
                            elif chatter_count < 5000:
                                viewer_count = round(chatter_count / .8)
                            else:
                                viewer_count = round(chatter_count / .8)
                                  
                            self._loggers[channel].info(response + self.bytes_seperator 
                                                + contents_name + self.bytes_seperator 
                                                + followers + self.bytes_seperator
                                                + bytes(str(chatter_count),'utf-8') + self.bytes_seperator
                                                + bytes(str(viewer_count),'utf-8') + self.bytes_seperator 
                                                + bytes(str(start_time),'utf-8') + self.bytes_seperator       
                                                + bytes(str(td_mins), 'utf-8')) 

                            if debug:
                                print(response)
                        elapsed = time() - now
                        if elapsed < 60/800:
                            sleep( (60/800) - elapsed) # Rate limit
                    else: # if not in ready_socks
                        pass
        if debug:
            print("Collected for " + str(time()-startTime) + " seconds")
        # Close sockets once not collecting data
        for channel in self.joined:
            self._sockets[channel].close()
        