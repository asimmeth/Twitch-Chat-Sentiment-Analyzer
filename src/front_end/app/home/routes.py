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


@blueprint.route('/recieve_streamer_visitors')
# @login_required
def recieve_streamer_visitors():
   streamer_choose_id = request.args.get('streamer_choose_id')
   streamer_choose_dt = request.args.get('streamer_choose_dt')
   print('---> test recieve_streamer_visitors: [START] --> ')
   print(streamer_choose_id)
   print(streamer_choose_dt)
   print('---> test recieve_streamer_visitors: [END] --> ')
   if streamer_choose_id == 'xQcOW':
    return "<p> 1,334,452 </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 2,345,453 </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 685,765 </p>" 


@blueprint.route('/streamer_visitors_perc')
# @login_required
def streamer_visitors_perc():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 5.25 </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> -1.25% </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 0.8% </p>" 

@blueprint.route('/streamer_visitors_earnings')
# @login_required
def streamer_visitors_earnings():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 300 </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 910 </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 870 </p>" 

@blueprint.route('/streamer_visitors_earnings_perc')
# @login_required
def streamer_visitors_earnings_perc():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 6.65% </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 0.1% </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 1.34% </p>" 

@blueprint.route('/livestreamed_min')
# @login_required
def livestreamed_min():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p>23,483</p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 1,289</p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 13,530</p>" 

@blueprint.route('/livestreamed_min_perc')
# @login_required
def livestreamed_min_perc():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 3.65% </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> -5.3%</p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 2.34% </p>"     

@blueprint.route('/streamer_chats_count')
# @login_required
def streamer_chats_count():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p>123,830</p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 76,890</p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 199,300</p>" 

@blueprint.route('/streamer_chats_perc')
# @login_required
def streamer_chats_perc():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 5.65% </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> -0.3%</p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 9.34% </p>"   



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

@blueprint.route('/recieve_streamer_visitors')
# @login_required
def total_chat_messages():
   streamer_choose_id = request.args.get('streamer_choose_id')
   streamer_choose_dt = request.args.get('streamer_choose_dt')
   print('---> test recieve_streamer_visitors: [START] --> ')
   print(streamer_choose_id)
   print(streamer_choose_dt)
   print('---> test recieve_streamer_visitors: [END] --> ')
    # set streamer name and datetime for now
    streamer_choose_id = 'tarik'
    streamer_choose_dt = '2022-07-26 22:57:57.779134'
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    total_messages_query = '''
                        select count(*) as total_messages, 
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(total_messages_query)
    message_count = cursor_obj.fetchall()
    conn.commit()
    conn.close()  

    return message_count[0][0] 

@blueprint.route('/recieve_streamer_visitors')
# @login_required
def average_viewers():
   streamer_choose_id = request.args.get('streamer_choose_id')
   streamer_choose_dt = request.args.get('streamer_choose_dt')
   print('---> test recieve_streamer_visitors: [START] --> ')
   print(streamer_choose_id)
   print(streamer_choose_dt)
   print('---> test recieve_streamer_visitors: [END] --> ')
    # set streamer name and datetime for now
    streamer_choose_id = 'tarik'
    streamer_choose_dt = '2022-07-26 22:57:57.779134'
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    average_views_query = '''
                        select round(avg(viewer_count)) as avg_viewers
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(average_views_query)
    view_count = cursor_obj.fetchall()
    conn.commit()
    conn.close()  

    return view_count[0][0] 

@blueprint.route('/recieve_streamer_visitors')
# @login_required
def new_followers():
   streamer_choose_id = request.args.get('streamer_choose_id')
   streamer_choose_dt = request.args.get('streamer_choose_dt')
   print('---> test recieve_streamer_visitors: [START] --> ')
   print(streamer_choose_id)
   print(streamer_choose_dt)
   print('---> test recieve_streamer_visitors: [END] --> ')
    # set streamer name and datetime for now
    streamer_choose_id = 'tarik'
    streamer_choose_dt = '2022-07-26 22:57:57.779134'
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    new_followers_query =  '''
                    with starting_followers as (
                        select follower_count
                        from chats_table_sentiment
                        where channel_name = {} and stream_date = {} 
                        order by date asc
                        limit 1)

                    ,ending_followers as (
                        select follower_count
                        from chats_table_sentiment
                        where channel_name = {} and stream_date = {}
                        order by date desc
                        limit 1
                        )

                    select * from starting_followers
                    UNION ALL select * from ending_followers

                    '''.format(channel_name, start_time, channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(new_followers_query)
    follower_count = cursor_obj.fetchall()
    follower_change = follower_count[1][0] - follower_count[0][0]
    conn.commit()
    conn.close()  

    return follower_change 


@blueprint.route('/recieve_streamer_visitors')
# @login_required
def new_followers():
   streamer_choose_id = request.args.get('streamer_choose_id')
   streamer_choose_dt = request.args.get('streamer_choose_dt')
   print('---> test recieve_streamer_visitors: [START] --> ')
   print(streamer_choose_id)
   print(streamer_choose_dt)
   print('---> test recieve_streamer_visitors: [END] --> ')
    # set streamer name and datetime for now
    streamer_choose_id = 'tarik'
    streamer_choose_dt = '2022-07-26 22:57:57.779134'
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    new_followers_query =  '''
                    with starting_followers as (
                        select subscriber_count
                        from chats_table_sentiment
                        where channel_name = {} and stream_date = {} 
                        order by date asc
                        limit 1)

                    ,ending_followers as (
                        select subscriber_count
                        from chats_table_sentiment
                        where channel_name = {} and stream_date = {}
                        order by date desc
                        limit 1
                        )

                    select * from starting_followers
                    UNION ALL select * from ending_followers

                    '''.format(channel_name, start_time, channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(new_followers_query)
    subscriber_count = cursor_obj.fetchall()
    subscriber_change = subscriber_count[1][0] - subscriber_count[0][0]
    conn.commit()
    conn.close()  

    return subscriber_change 
