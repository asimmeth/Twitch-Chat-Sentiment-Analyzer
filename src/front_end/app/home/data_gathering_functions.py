import sqlite3
import pandas as pd
import numpy as np

def get_subscriber_change(channel_name, start_time):
    """
    Query sql table and get the change in subscribers for selected stream
    input: channel_name, start_time
    output: subcriber change (int)
    """
    
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    new_subscriber_query =  '''
                    with starting_subscribers as (
                        select subscriber_count
                        from chats_table_demo
                        where channel_name = {} and stream_date = {} 
                        order by date asc
                        limit 1)

                    ,ending_subscribers as (
                        select subscriber_count
                        from chats_table_demo
                        where channel_name = {} and stream_date = {}
                        order by date desc
                        limit 1
                        )

                    select * from starting_subscribers
                    UNION ALL select * from ending_subscribers

                    '''.format(channel_name, start_time, channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(new_subscriber_query)
    subscriber_count = cursor_obj.fetchall()
    subscriber_change = subscriber_count[1][0] - subscriber_count[0][0]
    conn.commit()
    conn.close()
    
    return subscriber_change

def get_follower_change(channel_name, start_time):
    """
    Query sql table and get the change in followers for selected stream
    input: channel_name, start_time
    output: follower_change (int)
    """
     # set streamer name and datetime for now
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    new_followers_query =  '''
                    with starting_followers as (
                        select follower_count
                        from chats_table_demo
                        where channel_name = {} and stream_date = {} 
                        order by date asc
                        limit 1)

                    ,ending_followers as (
                        select follower_count
                        from chats_table_demo
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

def get_average_view_count(channel_name, start_time):
    """
    Query sql table and get the average number of viewers for selected stream
    input: channel_name, start_time
    output: view_count (int)
    """
    
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    average_views_query = '''
                        select round(avg(viewer_count)) as avg_viewers
                        from chats_table_demo
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(average_views_query)
    view_count = cursor_obj.fetchall()
    conn.commit()
    conn.close()  

    return view_count[0][0] 

def get_message_count(channel_name, start_time):
    """
    Query sql table and get the total number of chats for selected stream
    input: channel_name, start_time
    output: message_count (int)
    """
    
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    total_messages_query = '''
                        select count(*) as total_messages
                        from chats_table_demo
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(total_messages_query)
    message_count = cursor_obj.fetchall()
    conn.commit()
    conn.close()  


    return message_count[0][0]

def get_average_sentiment(channel_name, start_time):
    """
    Query sql table and get the average sentiment for selected stream
    input: channel_name, start_time
    output: average_sentiment (float)
    """
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    average_sentiment_query = '''
                        select avg(message_sentiment) as total_messages
                        from chats_table_demo
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(average_sentiment_query)
    average_sentiment = cursor_obj.fetchall()
    conn.commit()
    conn.close()  


    return average_sentiment[0][0] 

def get_number_chatters(channel_name, start_time):
    """
    Query sql table and get the average number of chatters for selected stream
    input: channel_name, start_time
    output: average_chatters (float)
    """
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    average_chatters_query = '''
                        select avg(chatter_count) as average_chatters
                        from chats_table_demo
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(average_chatters_query)
    average_chatters = cursor_obj.fetchall()
    conn.commit()
    conn.close()  


    return average_chatters[0][0] 

def recommendation(row):
    '''
    Basic recommendation engine. Each normalized category divided by the seconds spent times the weight. 
    
    Current weight configuration: 
    35% Sentiment Value
    30% Subs Gained
    25% Followers Gained
    10% Views
    '''
    value = ((0.10 * (row['avg_viewers'])/row['time']) 
            + (0.25 * (row['followers_change'])/row['time']) 
            + (0.30 * (row['subscriber_change'])/row['time']) 
            + (0.35 * (row['average_sentiment'])/row['time']))
    return value


def recommender_engine(channel_name, start_time):
    """ Queries sql table to get new followers, new subscribers, average viewers,
        average sentiment, and time by category. Runs the recommendation engine and
        outputs results.
        intput: channel_name, start_time
        output: recommendation_dict
    """
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')


    distinct_topics_query = '''
                        select distinct stream_topic 
                        from chats_table_demo
                        where channel_name = {} 
                        and stream_date = {}
                    '''.format(channel_name, start_time)

    cursor_obj = conn.cursor()
    cursor_obj.execute(distinct_topics_query)
    topics = cursor_obj.fetchall()
    
    followers_list = []
    subscriber_list = []
    for topic in topics[0]:
        query_topic = '\'' + topic + '\''
        new_followers_query =  '''
                    with starting_followers as (
                        select follower_count
                        from chats_table_demo
                        where channel_name = {} 
                        and stream_date = {} 
                        and stream_topic = {} 
                        order by date asc
                        limit 1)

                    ,ending_followers as (
                        select follower_count
                        from chats_table_demo
                        where channel_name = {}
                        and stream_date = {}
                        and stream_topic = {} 
                        order by date desc
                        limit 1
                        )

                    select * from starting_followers
                    UNION ALL select * from ending_followers
                    '''.format(channel_name, start_time, query_topic, channel_name, start_time, query_topic)
        cursor_obj = conn.cursor()
        cursor_obj.execute(new_followers_query)
        follower_count = cursor_obj.fetchall()
        follower_change = follower_count[1][0] - follower_count[0][0]
        followers_list.append(follower_change)

        new_subscriber_query =  '''
                    with starting_subscribers as (
                        select subscriber_count
                        from chats_table_demo
                        where channel_name = {} 
                        and stream_date = {} 
                        and stream_topic = {} 
                        order by date asc
                        limit 1)

                    ,ending_subscribers as (
                        select subscriber_count
                        from chats_table_demo
                        where channel_name = {}
                        and stream_date = {}
                        and stream_topic = {} 
                        order by date desc
                        limit 1
                        )

                    select * from starting_subscribers
                    UNION ALL select * from ending_subscribers

                    '''.format(channel_name, start_time, query_topic, channel_name, start_time, query_topic)
        cursor_obj = conn.cursor()
        cursor_obj.execute(new_subscriber_query)
        subscriber_count = cursor_obj.fetchall()
        subscriber_change = subscriber_count[1][0] - subscriber_count[0][0]
        subscriber_list.append(followers_list)
        
    grouped_stream_query = '''with grouped_stream as (
                select channel_name, 
                stream_topic, 
                avg(viewer_count) as avg_viewers, 
                max(stream_length) as max_minutes,
                min(stream_length) as min_minutes,
                round(avg(message_sentiment),2) as average_sentiment
                from chats_table_demo
                where channel_name = {}
                and stream_date = {}
                group by channel_name, stream_topic
                )
                select channel_name,
                stream_topic,
                round(avg_viewers) as avg_viewers, 
                average_sentiment,
                (max_minutes - min_minutes) as time
                from grouped_stream
                
                '''.format(channel_name, start_time)
    
    df = pd.read_sql_query(grouped_stream_query, conn)
    df['subscriber_change'] = np.array(subscriber_list)
    df['followers_change'] = np.array(subscriber_list)
    
    
    if len(topics) > 1:
        for col in ['avg_viewers','average_sentiment','subscriber_change','followers_change']:
       
            df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    
        df['score'] = df.apply(recommendation, axis = 1)
    else:
        df['score'] = 100
     
    conn.commit()
    conn.close()
    return df.to_dict()

