# -*- coding: utf-8 -*-
"""character_level.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1v69aJMgxLEMksoIybnofjshIgg8DqzA3
"""

import torch
import numpy as np 
import torch.nn as nn 
import torch.nn.functional as F

#DRIVE 
import os 
from google.colab import drive
drive.mount('/content/gdrive')
os.chdir('gdrive/My Drive')

#IMPORT THE DATASET
with open('datasets/anna.txt',"r") as f:
  dataset=f.read()

dataset[:100]

#unique character vocab.
chars = tuple(set(dataset))
#maps unique charater to interger
int2char = dict(enumerate(chars))
#which maps charaters to unique intergers
char2int = {ch:ii for ii, ch in int2char.items()}

encoded = np.array([char2int[ch] for ch in dataset])

encoded[:100] #31=>C, 66=> h, 57=>a,......

def one_hot_encoder(arr,n_labels):
   
       # Initialize the the encoded array
    one_hot = np.zeros((np.multiply(*arr.shape), n_labels), dtype=np.float32)
    
    # Fill the appropriate elements with ones
    one_hot[np.arange(one_hot.shape[0]), arr.flatten()] = 1.
    
    # Finally reshape it to get back to the original array
    one_hot = one_hot.reshape((*arr.shape, n_labels))
    
    return one_hot

test_seq=np.array([[3,5,1]])
one_hot = one_hot_encoder(test_seq,8)
print(one_hot)

def get_batches(arr,batch_size,seq_length):
  
  #number of character in batch = batch size *seq length
  n_batches = len(arr)//(batch_size*seq_length)
  #keeping only enough character to make full batches
  arr = arr[:n_batches*batch_size*seq_length]
  #reshaping the array 
  #rows= batch_size 
  #-1: placeholder 
  arr=arr.reshape((batch_size,-1))
  
  for n in range(0,arr.shape[1],seq_length):
    
    #taking all the rows, #batch_size
    #column dimension will be of seq_lenght in size
    x=arr[:,n:n+seq_length]
    
    y=np.zeros_like(x)
    
    try:
      y[:,:-1],y[:,-1] = x[:,1:], arr[:,n+seq_length]
    except IndexError:
      y[:,:-1],y[:,-1] = x[:,1:], arr[:,0]
    
    yield x,y

batches = get_batches(encoded,8,50)
x,y=next(batches)

#MODEL ARCHITECTURE
class CharacterRNN(nn.Module):
  
  def __init__(self,tokens,n_hidden=256,n_layers=2,drop_prob=.5,lr=.001):
    
    super(CharacterRNN,self).__init__()
    self.drop_prob = drop_prob
    self.n_hidden = n_hidden 
    self.n_layers= n_layers
    self.lr = lr
    
    self.chars = tokens
    self.int2char = dict(enumerate(self.chars))
    self.char2int = {ch:ii for ii, ch in self.int2char.items()}
    
    self.lstm = nn.LSTM(len(self.chars),hidden_size=n_hidden,num_layers=n_layers,dropout=drop_prob,batch_first=True)
    self.dropout=nn.Dropout(drop_prob)
    self.fc=nn.Linear(n_hidden,len(self.chars))
    
  def forward(self,x,hidden):
    
    #lstm produces lstm output and a new hidden state 
    r_output, hidden = self.lstm(x,hidden)
    
    out = self.dropout(r_output)
    
    #reshaping such that our last dimension is hidden dim
    out = out.contiguous().view(-1,self.n_hidden)
    
    out = self.fc(out)
    
    return out,hidden
  
  def init_hidden(self,batch_size):
    
    weight = next(self.parameters()).data
    
    hidden = (weight.new(self.n_layers,batch_size,self.n_hidden).zero_().cuda(),
             weight.new(self.n_layers,batch_size,self.n_hidden).zero_().cuda())
             
    return hidden



