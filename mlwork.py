import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay)

df = pd.read_csv("df_ml_final.csv")#loading my cleaned data

num_cols = ["release_year", "age", "is_recent", "duration_num", "is_tv", "is_us", "has_known_actor"]#the columns i want to use for my ml 
cat_cols =["rating", "genre_primary"]#CODE from Active book
X = df[num_cols + cat_cols].copy()
y = df["trending"]
X = X.dropna()#just cleaning my X and y needed for my ml so its not messy and uneven after so many charts
y = y.loc[X.index]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#took this whole chunk straight from the ActiveBook in codebench completely

numeric_pipe = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipe = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocess= ColumnTransformer(transformers=[
    ("num", numeric_pipe, num_cols),
    ("cat", categorical_pipe, cat_cols)
])

lr_model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("classifier", LogisticRegression(max_iter=1000, random_state=42))
])

lr_model.fit(X_train, y_train)
lr_preds = lr_model.predict(X_test)#all the way till here is directly from the activebook

print("Logistic Regression")
print("Accuracy:", accuracy_score(y_test, lr_preds))
print(classification_report(y_test, lr_preds, target_names=["Not Trending", "Trending"]))#found this in an implementation for sklearn

fig, ax =plt.subplots()#used Matplot and ConfusionDisplay to make charts on the model
ConfusionMatrixDisplay(confusion_matrix(y_test, lr_preds), display_labels=["Not Trending", "Trending"]).plot(ax=ax)
ax.set_title("Logistic Regression — Confusion Matrix")
fig.tight_layout()
fig.savefig("charts/11lrconfusionmatrix.png")
plt.close()

rf_model = Pipeline(steps=[#copied implementation from active book just changed name of Classifier
    ("preprocess", preprocess),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

rf_model.fit(X_train, y_train)#copied from activebook
rf_preds =rf_model.predict(X_test)

print("Random Forest")
print("Accuracy:", accuracy_score(y_test, rf_preds))
print(classification_report(y_test, rf_preds, target_names=["Not Trending", "Trending"]))

fig, ax = plt.subplots()# made a confusion visual here too
ConfusionMatrixDisplay(confusion_matrix(y_test, rf_preds),
                       display_labels=["Not Trending", "Trending"]).plot(ax=ax)
ax.set_title("Random Forest — Confusion Matrix")
fig.tight_layout()
fig.savefig("charts/13rfconfusionmatrix.png")
plt.close()


#this is stuff for the interactive predictor part i made, first i put it in a different file but the file was not working due to memory so i put it here and it worked
print("Enter details about the Netflix title:")

content_type = input("Type (Movie / TV Show): ").strip()#this is the basic input function in python so i can get user input and use it and store it. i cleaned it before storing so it works 
genre = input("Primary Genre (e.g. dramas, comedies, documentaries): ").strip().lower()
release_year= int(input("Release Year (e.g. 2021): ").strip())
rating = input("Content Rating (e.g. TV-MA, PG-13, R): ").strip()
country =input("Country of Origin (e.g. United States, India): ").strip()
duration = int(input("Duration (minutes if Movie, seasons if TV Show): ").strip())
has_known_actor= input("Does it feature a known/established actor? (yes / no): ").strip().lower()
age = 2026 - release_year #this is my calculations for what need to be cleaned before predicting
is_recent = int(release_year >= 2015)
is_tv =int(content_type == "TV Show")
is_us = int(country.lower() == "united states")
known =int(has_known_actor == "yes")#just the basic cleaning
input_df = pd.DataFrame([{"release_year":release_year,"age":age,"is_recent": is_recent,"duration_num": duration, "is_tv":is_tv, "is_us":is_us,"has_known_actor":known,"rating":rating,"genre_primary":genre}])
lr_prob =lr_model.predict_proba(input_df)[0][1]#just the function to predict on the stuff learned by the model
rf_prob= rf_model.predict_proba(input_df)[0][1]
avg_prob = (lr_prob + rf_prob) / 2

if lr_prob >= 0.5:#just basic above 50% means yes below means no in terms of trending content
    lr_verdict = "Likely to Trend"
else:
    lr_verdict = "Unlikely to Trend"
if rf_prob >= 0.5:#for each one, logistic, random, and avergae of both
    rf_verdict = "Likely to Trend"
else:
    rf_verdict = "Unlikely to Trend"
if avg_prob >= 0.5:
    avg_verdict = "Likely to Trend"
else:
    avg_verdict = "Unlikely to Trend"

print("RESULTS")#basic print my prediction result based on attributes entered
print("Logistic Regression:", round(lr_prob * 100, 1), lr_verdict)
print("Random Forest:", round(rf_prob * 100, 1), rf_verdict)
print("Average between both:", round(avg_prob * 100, 1), avg_verdict)