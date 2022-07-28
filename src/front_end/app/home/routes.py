# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import random
import os
import sqlite3

import pandas as pd

import src.scripts.data_gathering_functions as dg
from src.scripts.load_sentiment_model import load_model, tokenizer
from scripts.read_sentiments_from_db import read_sentiments

@blueprint.route('/index')
# @login_required
def index():

    return render_template('index.html', segment='index')

@blueprint.route('/<template>')
# @login_required
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        # Detect the current page
        segment = get_segment( request )

        # Serve the file (if exists) from app/templates/FILE.html
        return render_template( template, segment=segment )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

# Helper - Extract current page name from request 
def get_segment( request ): 

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment    

    except:
        return None  

@blueprint.route('/test')
# @login_required
def testfn():
    # GET request
    if request.method == 'GET':
        message = {'greeting':'Hello from Flask!!!'}
        return jsonify(message)  # serialize and use JSON headers
        # return render_template('index.html', msg=jsonify(message))
    # POST request
    if request.method == 'POST':
        # print(request.get_json())  # parse as JSON
        return 'Sucesss', 200
        # return render_template('index.html', msg=jsonify(message))


# @blueprint.route('/recieve_streamer_visitors')
# # @login_required
# def recieve_streamer_visitors():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    streamer_choose_dt = request.args.get('streamer_choose_dt')
#    print('---> test recieve_streamer_visitors: [START] --> ')
#    print(streamer_choose_id)
#    print(streamer_choose_dt)
#    print('---> test recieve_streamer_visitors: [END] --> ')
#    if streamer_choose_id == 'xQcOW':
#     return "<p> 1,334,452 </p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> 2,345,453 </p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 685,765 </p>" 


# @blueprint.route('/streamer_visitors_perc')
# # @login_required
# def streamer_visitors_perc():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p> 5.25 </p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> -1.25% </p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 0.8% </p>" 

# @blueprint.route('/streamer_visitors_earnings')
# # @login_required
# def streamer_visitors_earnings():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p> 300 </p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> 910 </p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 870 </p>" 

# @blueprint.route('/streamer_visitors_earnings_perc')
# # @login_required
# def streamer_visitors_earnings_perc():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p> 6.65% </p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> 0.1% </p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 1.34% </p>" 

# @blueprint.route('/livestreamed_min')
# # @login_required
# def livestreamed_min():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p>23,483</p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> 1,289</p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 13,530</p>" 

# @blueprint.route('/livestreamed_min_perc')
# # @login_required
# def livestreamed_min_perc():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p> 3.65% </p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> -5.3%</p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 2.34% </p>"     

# @blueprint.route('/streamer_chats_count')
# # @login_required
# def streamer_chats_count():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p>123,830</p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> 76,890</p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 199,300</p>" 

# @blueprint.route('/streamer_chats_perc')
# # @login_required
# def streamer_chats_perc():
#    streamer_choose_id = request.args.get('streamer_choose_id')
#    print(streamer_choose_id)
#    if streamer_choose_id == 'xQcOW':
#     return "<p> 5.65% </p>"
#    elif streamer_choose_id == 'Summit1G':
#     return "<p> -0.3%</p>"
#    elif streamer_choose_id == 'Shroud':
#     return "<p> 9.34% </p>"   



@blueprint.route('/read_random_sentiments')
# @login_required
def get_rand_sentiments():
   return read_sentiments(load_model(), tokenizer)


@blueprint.route('/refresh_sentiments')
# @login_required
def get_sentiments():
   num = random.uniform(0, 1)
   print('Hello from refresh_sentiments: ', num)
   return str(num)



@blueprint.route('/index')
# @login_required
def home():
   return render_template('index.html')


### Tiles Data Pull

@blueprint.route('/total_messages')
# @login_required
def total_chat_messages():
    """
    Calls get_message_count and returns the total message count of the stream
    output: total_messages (int)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    print('---> test recieve_streamer_visitors: [START] --> ')
    print(streamer_choose_id)
    print(streamer_choose_dt)
    print('---> test recieve_streamer_visitors: [END] --> ')
    
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    
    total_messages = dg.get_message_count(streamer_choose_id, streamer_choose_dt)
    
    return '<p>'+str(total_messages)+'</p>'

@blueprint.route('/average_viewers')
# @login_required
def average_viewers():
    """
    Calls get_average_view_count and returns the average view count of the stream``
    output: average_viewers (float)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    print('---> test recieve_streamer_visitors: [START] --> ')
    print(streamer_choose_id)
    print(streamer_choose_dt)
    print('---> test recieve_streamer_visitors: [END] --> ')
    
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    
    average_viewers = dg.get_average_view_count(streamer_choose_id, streamer_choose_dt)
    
    return '<p>'+str(round(average_viewers,2))+'</p>'

@blueprint.route('/followers_change')
# @login_required
def new_followers():
    """
    Calls get_follower_change and returns the change in followers from the start to end of the stream
    output: follower_change (int)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    print('---> test recieve_streamer_visitors: [START] --> ')
    print(streamer_choose_id)
    print(streamer_choose_dt)
    print('---> test recieve_streamer_visitors: [END] --> ')
    
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    
    follower_change = dg.get_follower_change(streamer_choose_id, streamer_choose_dt)
    
    return '<p>'+str(round(follower_change,2))+'</p>'


@blueprint.route('/subscriber_change')
# @login_required
def new_subscribers():
    """
    Calls get_subscriber_change and returns the change in subscribers from the start to end of the stream
    output: follower_change (int)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    print('---> test recieve_streamer_visitors: [START] --> ')
    print(streamer_choose_id)
    print(streamer_choose_dt)
    print('---> test recieve_streamer_visitors: [END] --> ')
    
    
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    subscriber_change = dg.get_subscriber_change(streamer_choose_id, streamer_choose_dt)
    return str(subscriber_change)+'+' if subscriber_change > 0 else str(subscriber_change)+'-'
    

@blueprint.route('/avg_sentiment')
# @login_required
def average_sentiment():
    """
    Calls get_average_sentiment and returns the average sentiment of the stream
    output: average_sentiment (float)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    print('---> avg_sentiment')
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    
    average_sentiment = dg.get_average_sentiment(streamer_choose_id, streamer_choose_dt)
    return '<p>'+str(round(average_sentiment, 2))+'</p>'

@blueprint.route('/avg_chatters')
# @login_required
def average_chatters():
    """
    Calls get_average_chatters and returns the average number of chatters in the chatroom
    output: follower_change (float)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    
    average_chatters = dg.get_average_chatters(streamer_choose_id, streamer_choose_dt)
    
    return '<p>'+str(round(average_chatters,2))+'</p>' 

@blueprint.route('/rec_engine_output_table')
# @login_required
def get_recommedations():
    """
    Calls recommender_engine and a dictionary of values and scores corresponding to the recommender model
    output: recommendation_dict (dict)
    """
    streamer_choose_id = request.args.get('streamer_choose_id')
    streamer_choose_dt = request.args.get('streamer_choose_dt')
    print('---> test recieve_streamer_visitors: [START] --> ')
    print(streamer_choose_id)
    print(streamer_choose_dt)
    print('---> test recieve_streamer_visitors: [END] --> ')
    
    
    # set streamer name and datetime for now
    streamer_choose_id = 'xeppaa'
    streamer_choose_dt = '2022-07-27'
    ################################################
    return dg.recommender_engine(streamer_choose_id, streamer_choose_dt)
