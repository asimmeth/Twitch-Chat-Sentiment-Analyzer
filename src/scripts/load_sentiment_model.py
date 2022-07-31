# from regex import R
from transformers import BertModel, BertTokenizer, AdamW, get_linear_schedule_with_warmup, BertForSequenceClassification
import torch
import os

from functools import lru_cache
# import torch.nn.functional as F
from torch import nn
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

PRE_TRAINED_MODEL_NAME = "veb/twitch-bert-base-cased-pytorch" #'models/veb/twitch-bert-base-cased-finetuned'
MAX_LEN = 160
tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)
class_names = ['negative', 'neutral', 'positive']

@lru_cache(maxsize=16)
def load_mlm_model():
  # If you are using the 
  # BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME, return_dict=False) #If you are using the 
  # Hugging Face transformers library, this error pops up when running code 
  # written in v3 on the transformers v4 library. 
  # To resolve it, simply add return_dict=False when loading the model 
  # https://stackoverflow.com/questions/65082243/dropout-argument-input-position-1-must-be-tensor-not-str-when-using-bert
  return BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME, return_dict=False) 

class SentimentClassifier(nn.Module):

  def __init__(self, n_classes):
    super(SentimentClassifier, self).__init__()
    self.bert = load_mlm_model() 
    self.drop = nn.Dropout(p=0.3)
    self.out = nn.Linear(self.bert.config.hidden_size, n_classes)
    
  def forward(self, input_ids, attention_mask):
    _, pooled_output = self.bert(
      input_ids=input_ids,
      attention_mask=attention_mask
    )
    output = self.drop(pooled_output)
    return self.out(output)

model = SentimentClassifier(len(class_names))

@lru_cache(maxsize=128)
def load_model():
  model.load_state_dict(torch.load('/home/w210/Twitch-chat-pioneers//models/twitch-bert-base-cased-sentiment-pytorch/BERT-base-cased-sentiment-pytorch_model.bin'))
  # model.load_state_dict(torch.load('/Users/Vaibhav_Beohar/Documents/VB_Mck_Docs/MIDS/W210/final_proj/Twitch-chat-pioneers/models/twitch-bert-base-cased-sentiment-pytorch/BERT-base-cased-sentiment-pytorch_model.bin'))
  return model
