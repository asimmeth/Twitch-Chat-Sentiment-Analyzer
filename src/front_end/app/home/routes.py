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
def get_id():
   # the_id = request.args.get('button_id')
   streamer_choose_id = request.args.get('streamer_choose_id')
   print(streamer_choose_id)
   if streamer_choose_id == 'xQcOW':
    return "<p> 1,334,452 </p>"
   elif streamer_choose_id == 'Summit1G':
    return "<p> 2,345,453 </p>"
   elif streamer_choose_id == 'Shroud':
    return "<p> 685,765 </p>" 
   
   #return "<p> Select a stream </p>" 


@blueprint.route('/refresh_sentiments')
@login_required
def get_sentiments():
   num = random.uniform(0, 1)
   print('Hello from refresh_sentiments: ', num)
   return str(num)
    #    streamer_choose_id = request.args.get('streamer_choose_id')
    #    print(streamer_choose_id)
    #    if streamer_choose_id == 'xQcOW':
    #     return "<p> 1,334,452 </p>"
    #    elif streamer_choose_id == 'Summit1G':
    #     return "<p> 2,345,453 </p>"
    #    elif streamer_choose_id == 'Shroud':
    #     return "<p> 685,765 </p>"    


@blueprint.route('/index')
@login_required
def home():
   return render_template('index.html')