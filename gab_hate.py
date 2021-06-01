# -*- coding: utf-8 -*-
"""Gab Hate

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ek2xG_lVk_dKP6TcVpoYP24BkElwrpht

Mount Google Drive so we can use our files.
"""

from google.colab import drive
drive.mount('/content/drive')

"""First, we simply read in our corpus."""

import pandas as pd

tsk = pd.read_csv('/content/drive/My Drive/gab data/GabHateCorpus_annotations.tsv', sep='\t')

# HD = assaults on human dignity
# CV = calls to violence
# VO = vulgar or offensive language

tsk

"""Now we'll take 80% of the data and make it our "training set", and the other 20% will be our "test set"."""

from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(tsk['Text'], tsk['Hate'], test_size=0.20, random_state=240)

y_test.values

from sklearn.feature_extraction.text import TfidfVectorizer
from keras.layers.core import Dense, Dropout
from nltk.corpus import stopwords
import nltk
from tensorflow.python.keras import models, layers

nltk.download("stopwords")

features = 5000

vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'), token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z]+\b', max_features=features)

vectorizer.fit(x_train.values)
tfidf = vectorizer.transform(x_train.values)

tfidf = pd.DataFrame(tfidf.toarray(), columns=vectorizer.get_feature_names())
tfidf

model = models.Sequential()

model.add(layers.Dense(1024, activation='relu', input_shape=(features,)))
model.add(layers.Dense(512, activation='relu'))
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer="adam", loss='binary_crossentropy', metrics=['accuracy'])

model.fit(tfidf.values, y_train.values, epochs=2, batch_size=350)

results = model.evaluate(vectorizer.transform(x_test.values).toarray(), y_test.values)

results

# for new data, vectorize the data the same way
# model.predict()

# convert the data into something useful (currently json)
import json
import pandas as pd

ohbaby = pd.read_json('/content/drive/My Drive/gab data/maga_after_10_01_2020', lines=True)

ohbaby.drop_duplicates(subset='content')

ohbaby

# make the text all pretty and nice
import re
!pip install emoji
import emoji

def give_emoji_free_text(text):
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  cleantext = give_emoji_free_text(cleantext)
  return cleantext


clean = [cleanhtml(x) for x in ohbaby['content'].values]

ridf = vectorizer.transform(clean)

ridf = pd.DataFrame(ridf.toarray(), columns=vectorizer.get_feature_names())

res = model.predict(ridf.values)

res

# res now contains our scores.
#NOTE: ohbaby['created_at'] contains the times of each post, ohbaby['content'] has the text and res contains the score.

# import numpy as np 
# import matplotlib.pyplot as plt
# from matplotlib.pyplot import figure

# figure(figsize=(8, 6), dpi=600)

# plt.title("Line graph") 
# plt.xlabel("Date") 
# plt.ylabel("Likelihood of it being hate") 
# plt.plot(ohbaby['created_at'], res, color ="red") 
# plt.show()

# import numpy

# a = np.array([ohbaby['content'].tolist(), ohbaby['created_at'].tolist(), res.tolist()])
# numpy.savetxt("output.log", a, delimiter='\t', header="Text,Date,Score", comments="", fmt="%s")


df = pd.DataFrame({"Text" : ohbaby['content'], "Date" : ohbaby['created_at'], "Score" : res.flatten()})
df.to_csv("submission2.csv", index=False)

# pd.DataFrame(a).to_csv('new_out.tsv', sep='\t')

print("Max:", res.max())
print("Min:", res.min())
print("Mean:", res.mean())
print("Median:", res.median())