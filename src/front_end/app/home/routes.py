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
# connection_obj = sqlite3.connect(os.getcwd()+'/src/front_end/db.sqlite3')

@blueprint.route('/index')
@login_required
def index():

    return render_template('index.html', segment='index')

@blueprint.route('/<template>')
@login_required
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
@login_required
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
@login_required
def recieve_streamer_visitors():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 1,334,452 </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 2,345,453 </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 685,765 </p>" 

@blueprint.route('/streamer_visitors_perc')
@login_required
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
@login_required
def streamer_visitors_earnings():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> $21.30 </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> $1.91 </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> $9.87 </p>" 

@blueprint.route('/streamer_visitors_earnings_perc')
@login_required
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
@login_required
def livestreamed_min():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p>234.83</p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 12.89</p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 135.30</p>" 

@blueprint.route('/livestreamed_min_perc')
@login_required
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
@login_required
def streamer_chats_count():
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p>123.83</p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 76.89</p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 199.30</p>" 

@blueprint.route('/streamer_chats_perc')
@login_required
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
@login_required
def get_rand_sentiments():
   result = read_sentiments(load_model(), tokenizer)
   print('Hello from refresh_sentiments: ', result)
   return result


@blueprint.route('/refresh_sentiments')
@login_required
def get_sentiments():
   num = random.uniform(0, 1)
   print('Hello from refresh_sentiments: ', num)
   return str(num)



@blueprint.route('/index')
@login_required
def home():
   return render_template('index.html')