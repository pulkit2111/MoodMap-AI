import joblib

MODEL_PATH=r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\models\spam_mail_detection_model.joblib'
VECTORIZER_PATH=r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\models\spam_vectorizer.joblib'

feature_extraction = joblib.load(VECTORIZER_PATH)
model = joblib.load(MODEL_PATH)

def spamCheck(message):
    # Vectorize the message using the loaded vectorizer
    message_vectorized = feature_extraction.transform([message])
    
    # Predict the sentiment using the loaded model
    prediction = model.predict(message_vectorized)[0]
    if(prediction==0):
        return 'YES'
    else:
        return 'NO'