import transformers
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup, BertForSequenceClassification
import torch

import numpy as np
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from collections import defaultdict
from textwrap import wrap

import tensorflow as tf
from torch import nn, optim
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

PRE_TRAINED_MODEL_NAME = "veb/twitch-bert-base-cased-pytorch" #'models/veb/twitch-bert-base-cased-finetuned'
MAX_LEN = 160
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)


class SentimentClassifier(nn.Module):

  def __init__(self, n_classes):
    super(SentimentClassifier, self).__init__()
    self.bert = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME, return_dict=False) #If you are using the 
     #Hugging Face transformers library, this error pops up when running code 
     # written in v3 on the transformers v4 library. 
     # To resolve it, simply add return_dict=False when loading the model 
     # https://stackoverflow.com/questions/65082243/dropout-argument-input-position-1-must-be-tensor-not-str-when-using-bert
    self.drop = nn.Dropout(p=0.3)
    self.out = nn.Linear(self.bert.config.hidden_size, n_classes)
    
  def forward(self, input_ids, attention_mask):
    _, pooled_output = self.bert(
      input_ids=input_ids,
      attention_mask=attention_mask
    )
    output = self.drop(pooled_output)
    return self.out(output)

class_names = ['negative', 'neutral', 'positive']

model = SentimentClassifier(len(class_names))
model.load_state_dict(torch.load('../models/twitch-bert-base-cased-sentiment-pytorch/BERT-base-cased-sentiment-pytorch_model.bin'))

review_text  = str(input("Enter review text:"))
#review_text = "ted cruz"

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

output = model(input_ids, attention_mask)
_, prediction = torch.max(output, dim=1)
# print(f'_____: {_}')
# print(f'prediction: {output}')

_, preds = torch.max(output, dim=1)
# print(_)
# print(preds)
# print('-----> ', output.softmax(dim=-1))

print(f'Review text: {review_text}')
print(f'Sentiment  : {class_names[prediction]}')