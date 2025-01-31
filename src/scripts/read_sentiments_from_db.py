import torch
import sqlite3
import json

def read_sentiments(model, tokenizer):
	# conn = sqlite3.connect('/home/w210/Twitch-chat-pioneers/src/front_end/db.sqlite3')
	conn = sqlite3.connect('../front_end/db.sqlite3')


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

	prob = torch.nn.functional.softmax(output, dim=1)
	top_prob = prob.topk(1, dim=1)[0].data[0].numpy()
	_, prediction = torch.max(output, dim=1)

	pred_class = class_names[prediction]
	pred_class = '<h1 style="font-family:verdana;color:green;">'+pred_class+'</h1>' if pred_class=='Positive' \
						else '<h1 style="font-family:verdana;color:red;">'+pred_class+'</h1>' \
							if pred_class=='Negative' else '<h1 style="font-family:verdana;color:gray;">'+pred_class+'</h1>'
	pred_proba = format(top_prob[0], '.6f') if pred_class=='Positive' else format(top_prob[0] * -1, '.6f') if pred_class=='Negative' else 0
	# print(f'Review text: {msg}')
	# print(f'Sentiment  : {class_names[prediction]}')

	return json.dumps([{
		# 'sentiment_display': '<p>Sentiment for: <B>'+ msg + '</B> sent by user: <B>'+ uname + '</B> is: <B>' + pred_class + '</B></p>', 
		# 'prob_score' : pred_proba
		'sentiment_display': '<p> "'+ msg + ' " <i> -'+uname+'</i></p>',
		'user': '<p> -'+uname+'</p>',
		'pred_class':pred_class, 
		'prob_score' : pred_proba		
	}])
