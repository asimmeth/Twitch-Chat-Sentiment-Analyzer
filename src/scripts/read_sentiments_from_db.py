import torch
import sqlite3

def read_sentiments(model, tokenizer):
	conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')

	MAX_LEN = 160
	class_names = ['Negative', 'Neutral', 'Positive']
	cursor_obj = conn.cursor()
	cursor_obj.execute("select text, username from streamer_data_sqlite_chats order by RANDOM() limit 1")
	output = cursor_obj.fetchall()
	msg = output[0][0]
	uname = output[0][1]
	conn.commit()
	conn.close()  

	encoded_review = tokenizer.encode_plus(
		msg,
		max_length=MAX_LEN,
		add_special_tokens=True,
		return_token_type_ids=False,
		pad_to_max_length=True,
		return_attention_mask=True,
		return_tensors='pt',
		)

	input_ids = encoded_review['input_ids']
	attention_mask = encoded_review['attention_mask']

	output = model(input_ids, attention_mask)
	_, prediction = torch.max(output, dim=1)

	# print(f'Review text: {msg}')
	# print(f'Sentiment  : {class_names[prediction]}')

	return '<p>Sentiment for: <B>'+ msg + '</B> sent by user: <B>'+ uname + '</B> is: <B>' + class_names[prediction] + '</B></p>'
