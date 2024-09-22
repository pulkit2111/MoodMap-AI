# from zipfile import ZipFile
# dataset = 'sentiment140.zip'
# with ZipFile(dataset, 'r') as zip:
#     zip.extractall()
#     print('Dataset extracted.')

import os
import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# import nltk
# nltk.download('stopwords')
# print(stopwords.words('hinglish'))

# loading data from csv file to pandas dataframe
# column_names=['target', 'id', 'date', 'flag', 'user', 'text']
# twitter_data=pd.read_csv('training.1600000.processed.noemoticon.csv',names=column_names, encoding='ISO-8859-1')
# print(twitter_data.head())

# #counting the number of missing values in the dataset
# print(twitter_data.isnull().sum())

# #checking the distribution of target column
# twitter_data['target'].value_counts()

#convert the target 4 to 1
# twitter_data.replace({'target':{4:1}}, inplace=True) #0 means negative tweet, 1 means positive tweet

# DATA PREPROCESSING : stemming- process of reducing a word into its root word
port_stem=PorterStemmer()
def stemming(content): #content here means tweet
    stemmed_content=re.sub('[^a-zA-Z]',' ',content) #we only want letters so remove any other character apart from alphabets
    stemmed_content=stemmed_content.lower() #lowercase all alphabets
    stemmed_content=stemmed_content.split() #split the tweet into words, stemmed content is now a list of words
    stemmed_content=[port_stem.stem(word) for word in stemmed_content if not word in stopwords.words('english')] #stem a word to its root word if it doesnot belong to stopwords
    stemmed_content=' '.join(stemmed_content)

    return stemmed_content

# File path to save/load stemmed data
stemmed_file_path = 'twitter_data_stemmed.csv'

# # Check if the preprocessed data already exists
# if os.path.exists(stemmed_file_path):
#     # Load the stemmed data from the CSV file
#     twitter_data = pd.read_csv(stemmed_file_path)
#     print("Loaded stemmed data from CSV.")
# else:
#     # If not, preprocess and save it
#     print("Stemmed data not found. Stemming in progress...")
    
#     # Loading data from CSV
#     column_names = ['target', 'id', 'date', 'flag', 'user', 'text']
#     twitter_data = pd.read_csv('training.1600000.processed.noemoticon.csv', names=column_names, encoding='ISO-8859-1')

#     # Convert the target 4 to 1 (0 = negative, 1 = positive)
#     twitter_data.replace({'target': {4: 1}}, inplace=True)

#     # Apply stemming function to each tweet
#     twitter_data['stemmed_content'] = twitter_data['text'].apply(stemming)

#     # Save the stemmed data to a CSV file for future use
#     twitter_data[['target', 'stemmed_content']].to_csv(stemmed_file_path, index=False)
#     print("Stemming completed and saved to CSV.")

# Display first few rows of stemmed content
# print(twitter_data)

twitter_data = pd.read_csv(stemmed_file_path)
twitter_data['stemmed_content'].fillna('', inplace=True)

X=twitter_data['stemmed_content']
Y=twitter_data['target']

# splitting the data into training data and test data
X_train, X_test, Y_train, Y_test=train_test_split(X,Y,test_size=0.2, stratify=Y, random_state=2) #test size means % of data that will be tested, stratify means that we want equal proportion of 0 and 1 target values in our training data and test data

# converting the textual data into numerical data
# vectorizer=TfidfVectorizer() #TfidVectorizer assigns some importance to every word in the whole dataset

# X_train=vectorizer.fit_transform(X_train) #use training data to assign importance to words, here two processes are done fitting and transforming fitting assigns values and transforming transforms words into numerical form
# X_test=vectorizer.transform(X_test) #based on the above fitting , transform current test data

# print(X_train)
# print(X_test)

#TRAINING and VECTORIZING THE ML MODEL - LOGISTIC REGRESSION MODEL
MODEL_PATH = 'models/logistic_regression_model.joblib'
VECTORIZER_PATH = 'models/tfidf_vectorizer.joblib'

# model=LogisticRegression(max_iter=1000)
# model.fit(X_train, Y_train)

# Check if the model and vectorizer already exist
if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    # Load the saved vectorizer and model
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)
    print("Loaded model and vectorizer from disk.")
else:
    print("Training new model and vectorizer...")
    
    # Initialize the TfidfVectorizer
    vectorizer = TfidfVectorizer()
    
    # Convert the textual data into numerical data
    X_train = vectorizer.fit_transform(X_train)  # Fit and transform on training data
    X_test = vectorizer.transform(X_test)  # Transform test data based on training fit
    
    # Initialize and train the Logistic Regression model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, Y_train)
    
    # Save the trained model and vectorizer to disk
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_PATH}")


# Convert the textual data into numerical data
X_train = vectorizer.fit_transform(X_train)  # Fit and transform on training data
X_test=["kill you fuck you"]
X_test = vectorizer.transform(X_test)  # Transform test data based on training fit
    
# Model evaluation
# X_train_prediction = model.predict(X_train)
# training_data_accuracy=accuracy_score(Y_train, X_train_prediction)
# print('Accuracy score : ', training_data_accuracy)

# X_test_prediction = model.predict(X_test)
# test_data_accuracy=accuracy_score(Y_test, X_test_prediction)
# print('Accuracy score : ', test_data_accuracy)

prediction=model.predict(X_test[0])
print(prediction)