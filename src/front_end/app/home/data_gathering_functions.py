import sqlite3

def get_follower_change(channel_name, start_time):
    
    
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

def get_subscriber_change(channel_name, start_time):
    
     # set streamer name and datetime for now
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

def get_average_view_count(channel_name, start_time):
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    average_views_query = '''
                        select round(avg(viewer_count)) as avg_viewers
                        from chats_table_sentiment
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(average_views_query)
    view_count = cursor_obj.fetchall()
    conn.commit()
    conn.close()  

    return view_count[0][0] 

def get_message_count(channel_name, start_time):
    streamer_choose_id = 'tarik'
    streamer_choose_dt = '2022-07-26 22:57:57.779134'
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    
    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
    
    total_messages_query = '''
                        select count(*) as total_messages
                        from chats_table_sentiment
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(total_messages_query)
    message_count = cursor_obj.fetchall()
    conn.commit()
    conn.close()  


    return message_count[0][0] 