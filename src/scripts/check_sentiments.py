from load_sentiment_model import load_model
from transformers import BertTokenizer
import torch
import time
# import random
# import string
import sqlite3
import os

begin = time.time()
PRE_TRAINED_MODEL_NAME = "veb/twitch-bert-base-cased-pytorch" #'models/veb/twitch-bert-base-cased-finetuned'
MAX_LEN = 160
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
class_names = ['negative', 'neutral', 'positive']

review_text  = str(input("Enter review text:"))

encoded_review = tokenizer.encode_plus(
review_text,
max_length=MAX_LEN,
add_special_tokens=True,
return_token_type_ids=False,
pad_to_max_length=True,
return_attention_mask=True,
return_tensors='pt',
)

input_ids = encoded_review['input_ids']
attention_mask = encoded_review['attention_mask']

model = load_model()
output = model(input_ids, attention_mask)
_, prediction = torch.max(output, dim=1)
# print(f'_____: {_}')
# print(f'prediction: {output}')

prob = torch.nn.functional.softmax(output, dim=1)
top_prob = prob.topk(1, dim=1)[0].data[0].numpy()
print(str(format(top_prob[0]* 100, '.2f'))+'%')

_, preds = torch.max(output, dim=1)
# print(_)
# print(preds)
# print('-----> ', output.softmax(dim=-1))

print(f'Review text: {review_text}')
print(f'Sentiment  : {class_names[prediction]}')

end = time.time()
print('Time taken for execution --> ', (end - begin))


# print(os.getcwd()+'/src/front_end/db.sqlite3')
# connection_obj = sqlite3.connect(os.getcwd()+'/src/front_end/db.sqlite3')
# cursor_obj = connection_obj.cursor()
# cursor_obj.execute("select text, username from streamer_data_sqlite_chats order by RANDOM() limit 1")
# output = cursor_obj.fetchall()
# print(output[0][0])
# print(output[0][1])
# for row in output:
#   print(row[0])
#   print(row[1])
# connection_obj.commit()
# connection_obj.close()  
