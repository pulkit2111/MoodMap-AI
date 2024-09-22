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

# DATA PREPROCESSING : stemming- process of reducing a word into its root word
port_stem=PorterStemmer()
def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"  # other symbols
                               u"\U000024C2-\U0001F251"  # enclosed characters
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def stemming(content):  # content here means tweet
    if pd.isnull(content):
        return ''  # Return empty string for NaN
    
    # Load stop words from file
    with open(r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\stop_hinglish.txt', 'r') as f:
        stop_words = f.read().splitlines()  # Convert stop words into a list
    
    # Remove emojis from the content
    content = remove_emojis(content)
    
    # Remove non-alphabet characters and lowercase the text
    stemmed_content = re.sub('[^a-zA-Z]', ' ', content)
    stemmed_content = stemmed_content.lower()
    
    # Split into words and remove stop words
    stemmed_content = stemmed_content.split()
    stemmed_content = [port_stem.stem(word) for word in stemmed_content if word not in stop_words]
    
    # Join the words back into a string
    stemmed_content = ' '.join(stemmed_content)
    
    return stemmed_content

# File path to save/load stemmed data
stemmed_file_path = r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\TwitterPostAnalysis\twitter_data_stemmed.csv'

# Check if the preprocessed data already exists
if os.path.exists(stemmed_file_path):
    # Load the stemmed data from the CSV file
    twitter_data = pd.read_csv(stemmed_file_path)
    print("Loaded stemmed data from CSV.")
else:
    # If not, preprocess and save it
    print("Stemmed data not found. Stemming in progress...")
    # Loading data from CSV
    column_names = ['target', 'id', 'date', 'flag', 'user', 'text']
    twitter_data = pd.read_csv('training.1600000.processed.noemoticon.csv', names=column_names, encoding='ISO-8859-1')
    # Convert the target 4 to 1 (0 = negative, 1 = positive)
    twitter_data.replace({'target': {4: 1}}, inplace=True)
    # Apply stemming function to each tweet
    twitter_data['stemmed_content'] = twitter_data['text'].apply(stemming)
    # Save the stemmed data to a CSV file for future use
    twitter_data[['target', 'stemmed_content']].to_csv(stemmed_file_path, index=False)
    print("Stemming completed and saved to CSV.")

twitter_data = pd.read_csv(stemmed_file_path)
twitter_data['stemmed_content'].fillna('', inplace=True)
X=twitter_data['stemmed_content']
Y=twitter_data['target']

# splitting the data into training data and test data
X_train, X_test, Y_train, Y_test=train_test_split(X,Y,test_size=0.2, stratify=Y, random_state=2) #test size means % of data that will be tested, stratify means that we want equal proportion of 0 and 1 target values in our training data and test data

#TRAINING and VECTORIZING THE ML MODEL - LOGISTIC REGRESSION MODEL
MODEL_PATH = r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\TwitterPostAnalysis\models\logistic_regression_model.joblib'
VECTORIZER_PATH = r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\TwitterPostAnalysis\models\tfidf_vectorizer.joblib'

# Check if the model and vectorizer already exist
if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    # Load the saved vectorizer and model
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)
    X_test = vectorizer.transform(X_test)  # Transform test data based on training fit
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


# Model evaluation
X_test_prediction = model.predict(X_test)
test_data_accuracy=accuracy_score(Y_test, X_test_prediction)
print('Accuracy score : ', test_data_accuracy)
