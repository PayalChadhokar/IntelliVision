import joblib

# Load the already trained model
model = joblib.load("models/crime_classifier.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

# New complaints for testing
complaints = [
    "Someone stole my mobile phone from my bag while I was travelling.",
    "I received a fake bank call and lost money from my account.",
    "Someone broke into my house and stole my jewellery.",
    "A person has been following me repeatedly near my college.",
    "My motorcycle was stolen from outside my house.",
    "Someone attacked me during an argument and injured me.",
    "I received threatening messages from an unknown person online.",
    "My brother has been missing since yesterday.",
    "Someone is demanding money and threatening me.",
    "Someone used my personal details to create an account without my permission."
]

# Convert complaints into TF-IDF
complaints_tfidf = vectorizer.transform(complaints)

# Predict crime type
predictions = model.predict(complaints_tfidf)

# Display results
print("\n===================================")
print("NEW COMPLAINT TESTING")
print("===================================\n")

for i, (complaint, prediction) in enumerate(
    zip(complaints, predictions), start=1
):
    print(f"{i}. Complaint:")
    print(complaint)
    print(f"Predicted Crime: {prediction}")
    print("-----------------------------------")
    