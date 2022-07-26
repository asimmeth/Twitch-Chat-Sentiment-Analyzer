import sqlite3
import json

def get_dashboard_data(channel_name, start_time):
	
    channel_name = '\'' + channel_name + '\''
    stream_title = '\'' + start_time + '\''
    channel_name = '\'tarik\''


    conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')

    query = '''select count(*) as total_messages, 
                    avg(viewer_count) as avg_viewers,
                        from chats_table
                        where channel_name = {}
                        '''.format(channel_name)

    cursor_obj = conn.cursor()
    cursor_obj.execute(query)
    output = cursor_obj.fetchall()
    msg_count = output[0][0]
    conn.commit()
    conn.close()  


    return json.dumps([{
        'total_messages': msg_count }])