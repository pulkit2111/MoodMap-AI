import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

MODEL_PATH=r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\models\spam_mail_detection_model.joblib'
VECTORIZER_PATH=r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\models\spam_vectorizer.joblib'

#DATA COLLECTION AND PREPROCESSING

raw_mail_data=pd.read_csv('mail_data.csv')

#replace null values with a null string
mail_data=raw_mail_data.where((pd.notnull(raw_mail_data)), '')

#label spam mail as 0 and ham mail as 1
mail_data.loc[mail_data['Category']=='spam', 'Category', ]=0
mail_data.loc[mail_data['Category']=='ham', 'Category', ]=1

#separating the data as texts and label
X=mail_data['Message']
Y=mail_data['Category']

#splitting data into training data and test data
X_train, X_test, Y_train, Y_test=train_test_split(X,Y,test_size=0.2, random_state=3)

#FAETURE EXTRACTION

##converting the text data to feature vectors that can be used as input to Logistic regression model
# feature_extraction= TfidfVectorizer(min_df=1, stop_words='english', lowercase=True) #mid_df is the minimum score a word should have to be considered
# X_train_features=feature_extraction.fit_transform(X_train)
# X_test_features=feature_extraction.transform(X_test)
# joblib.dump(feature_extraction, VECTORIZER_PATH)
feature_extraction = joblib.load(VECTORIZER_PATH)
X_test_features=feature_extraction.transform(X_test)

#convert Y_train and Y_test values as integers
Y_train=Y_train.astype('int')
Y_test=Y_test.astype('int')

##TRAINING LOGISTIC REGRESSION MODEL
# model=LogisticRegression()
# model.fit(X_train_features, Y_train)
# joblib.dump(model, MODEL_PATH)
model = joblib.load(MODEL_PATH)

prediction_on_test_data=model.predict(X_test_features)

accuracy=accuracy_score(Y_test, prediction_on_test_data)
print(accuracy)
