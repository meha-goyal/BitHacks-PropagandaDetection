# -*- coding: utf-8 -*-
"""Bit.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1K7tbCW4C5C_C4fkIiq_jra0HNNAYClEz
"""

import flask
import pickle
import pandas as pd
import math
from torchtext.vocab import GloVe
import numpy as np
from sklearn.linear_model import LogisticRegression
pip install torchtext

# Use pickle to load in the pre-trained model
with open(f'model/tweet_class_model.pkl', 'rb') as f:
  model = pickle.load(f)

# Initialise the Flask app
app = flask.Flask(__name__, template_folder='templates')

# Set up the main route
@app.route('/', methods=['GET', 'POST'])

def get_normalized_count(text, phrase):
    return math.log(1 + text.count(phrase.lower()))

def keyword_featurizer(text):
    features = {}
    
    keywords = ['clinton', 'soros', 'liberal', 'antifa', 'mainstream', 'protesters', 'hillary', 'God', 'wiretap', 'riot', 'obama', 'troll', 'leftist']
    
    for keyword in keywords:
      features[keyword + ' keyword'] = get_normalized_count(text, keyword)
    
    return features

VEC_SIZE = 300
glove = GloVe(name='6B', dim=VEC_SIZE)

# Returns word vector for word if it exists, else return None.
def get_word_vector(word):
    try:
      return glove.vectors[glove.stoi[word.lower()]].numpy()
    except KeyError:
      return None

def glove_transform(tweet_content):
    X = np.zeros((len(tweet_content), VEC_SIZE))
    for i, tweet_content in enumerate(tweet_content):
        found_words = 0.0
        tweet_content = tweet_content.strip()
        for word in tweet_content.split(): 
            vec = get_word_vector(word)
            if vec is not None:
                found_words += 1
                X[i] += vec

        if found_words > 0:
            X[i] /= found_words
            
    return X

def main():
    if flask.request.method == 'GET':
        # Just render the initial form, to get input
        return(flask.render_template('index.html'))
    
    else:
        # Extract the input
        tweet = flask.request.form.get("tweet", False)
        # Make DataFrame for model
        input_variable = pd.DataFrame([[tweet]],
                                       columns=['tweet'],
                                       dtype=str,
                                       index=['input'])

        
        def dict_to_features(features_dict):
            X = np.array(list(features_dict.values())).astype('float')
            X = X[np.newaxis, :]
            return X
        def featurize_data(text):
          keyword_X = dict_to_features(keyword_featurizer(text))
          bow_X = vectorizer.transform(text).todense()
          glove_X = glove_transform(text)
          X_list = [keyword_X, bow_X, glove_X]
          X = np.concatenate(X_list, axis=1)
          return X

        curr_X = featurize_data([input_variable])
        
        # Get the model's prediction
        prediction = model.predict(curr_X)[0]
    
        # Render the form again, but add in the prediction and remind user
        # of the values they input before
        return flask.render_template('index.html',
                                     original_input={'Tweet': tweet},
                                     result=prediction
                                     )

if __name__ == '__main__':
    app.run(debug = True)


