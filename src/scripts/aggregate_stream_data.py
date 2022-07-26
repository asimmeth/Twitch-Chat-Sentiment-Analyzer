import sqlite3
import json

def get_dashboard_data(channel_name, start_time):
	
    channel_name = '\'' + channel_name + '\''
    start_time = '\'' + start_time + '\''
    channel_name = '\'tarik\''


    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')

    # Calculate Average Views and Total Messages
    avg_views_total_messages_query = '''select count(*) as total_messages, 
                    round(avg(viewer_count)) as avg_viewers,
                    max(stream_length) as stream_length_minutes
                        from chats_table
                        where channel_name = {} and stream_date = {}
                        '''.format(channel_name, start_time)
    
    # Calculate followers at start and end of stream
    followers_subscribers_query =  '''
                        with starting_followers as (
                            select follower_count, subscriber_count
                            from chats_table
                            where channel_name = {} and stream_date = {} 
                            order by date asc
                            limit 1)

                        ,ending_followers as (
                            select follower_count, subscriber_count
                            from chats_table
                            where channel_name = {} and stream_date = {}
                            order by date desc
                            limit 1
                            )
                        
                        
                        select * from starting_followers
                        UNION ALL select * from ending_followers
                        
                        '''.format(channel_name, start_time, channel_name, start_time)
    
    
    cursor_obj = conn.cursor()
    cursor_obj.execute(avg_views_total_messages_query)
    averages_output = cursor_obj.fetchall()
    
    cursor_obj.execute(followers_subscribers_query)
    followers_subscribers = cursor_obj.fetchall()
    followers_gained = followers_subscribers[1][0] - followers_subscribers[0][0]
    followers_pct_change = round(abs(followers_gained) / followers_subscribers[0][0],4)*100
    subscribers_gained = followers_subscribers[1][1] - followers_subscribers[0][1]
    subscriber_pct_change = round(abs(subscribers_gained) / followers_subscribers[0][1],4) *100
    
    recommender_query = '''with grouped_stream as (
                    select channel_name, 
                    stream_topic, 
                    avg(viewer_count) as avg_viewers, 
                    max(follower_count) as max_followers,
                    min(follower_count) as min_followers,
                    max(subscriber_count) as max_subscribers,
                    min(subscriber_count) as min_subscribers,
                    max(stream_length) as max_minutes,
                    min(stream_length) as min_minutes
                    from chats_table
                    where channel_name = {}
                    group by channel_name, stream_topic
                    )
            select channel_name,
            stream_topic,
            avg_viewers, 
            (max_followers - min_followers) as followers_gained,
            (max_subscribers - min_subscribers) as subscribers_gained,
            (max_minutes - min_minutes) as time
            from grouped_stream
                    '''.format(channel_name)
    
    
    
    conn.commit()
    conn.close()  


    return json.dumps([{
        'total_messages': averages_output[0][0],
        'average_viewers': averages_output[0][1],
        'new_followers': followers_gained,
        'follower_pct_change': followers_pct_change,
        'subscribers_gained': subscribers_gained,
        'subscriber_pct_change': subscriber_pct_change
    }])