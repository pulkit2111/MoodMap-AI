import pandas as pd
import re
from nltk.stem.porter import PorterStemmer
import joblib

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

MODEL_PATH = r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\TwitterPostAnalysis\models\logistic_regression_model.joblib'
VECTORIZER_PATH = r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\TwitterPostAnalysis\models\tfidf_vectorizer.joblib'

vectorizer = joblib.load(VECTORIZER_PATH)
model = joblib.load(MODEL_PATH)

def sentimentAnalyze(message):
    stemmed_message = stemming(message)
    if not stemmed_message.strip():
        return None
    
    # Vectorize the message using the loaded vectorizer
    message_vectorized = vectorizer.transform([stemmed_message])
    
    # Predict the sentiment using the loaded model
    prediction = model.predict(message_vectorized)[0]
    return prediction
