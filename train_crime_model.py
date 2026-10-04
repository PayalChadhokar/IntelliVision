import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# -----------------------------------------
# 1. Load dataset
# -----------------------------------------
DATASET_PATH = "database/IntelliVision_Improved_Complaints_Dataset.csv"

df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully!")
print("Number of records:", len(df))

# -----------------------------------------
# 2. Select input and target
# -----------------------------------------

X = df["Complaint_Text"].fillna("")
y = df["Crime_Type"]

# -----------------------------------------
# 3. Split dataset
# -----------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# -----------------------------------------
# 4. TF-IDF
# -----------------------------------------

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    max_features=5000
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# -----------------------------------------
# 5. Train Logistic Regression
# -----------------------------------------

model = LogisticRegression(
    max_iter=1000
)

model.fit(X_train_tfidf, y_train)

print("\nModel training completed!")

# -----------------------------------------
# 6. Prediction
# -----------------------------------------

y_pred = model.predict(X_test_tfidf)

# -----------------------------------------
# 7. Accuracy
# -----------------------------------------

accuracy = accuracy_score(y_test, y_pred)

print("\n===================================")
print("MODEL EVALUATION")
print("===================================")

print(f"Accuracy: {accuracy:.4f}")
print(f"Accuracy Percentage: {accuracy * 100:.2f}%")

# -----------------------------------------
# 8. Classification report
# -----------------------------------------

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -----------------------------------------
# 9. Confusion matrix
# -----------------------------------------

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# -----------------------------------------
# 10. Save model
# -----------------------------------------

joblib.dump(
    model,
    "models/crime_classifier.pkl"
)

joblib.dump(
    vectorizer,
    "models/tfidf_vectorizer.pkl"
)

print("\n===================================")
print("FILES SAVED")
print("===================================")
print("models/crime_classifier.pkl")
print("models/tfidf_vectorizer.pkl")