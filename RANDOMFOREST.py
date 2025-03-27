import pandas as pd
import numpy as np
import ast
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss, classification_report

# Display options for better visibility
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1000)

# Load the Excel file (assumes "bill_id" column exists)
df = pd.read_excel("data_with_status_doc_prob.xlsx")
print("Columns in Excel:", df.columns.tolist())
print(df.head())

# Safely parse seat_counts stored as a stringified dictionary
def parse_seat_counts(val):
    if pd.isnull(val):
        return {}
    try:
        return ast.literal_eval(val)
    except Exception:
        return {}

df["seat_counts_parsed"] = df["seat_counts"].apply(parse_seat_counts)
df["Labour_seats"] = df["seat_counts_parsed"].apply(lambda d: d.get("Labour", 0))
df["Conservative_seats"] = df["seat_counts_parsed"].apply(lambda d: d.get("Conservative", 0))
df["LibDem_seats"] = df["seat_counts_parsed"].apply(lambda d: d.get("Liberal Democrat", 0))

# Filter data to model rows (using progress_status of 1 or 2)
df_model = df[df["progress_status"].isin([1, 2])].copy()

# Function to parse the doc_prob column (string to list of floats)
def parse_doc_prob(val):
    if pd.isnull(val):
        return []
    try:
        val = val.strip("[]")
        parts = val.split()
        return [float(x) for x in parts]
    except Exception:
        return []

df_model["doc_prob_parsed"] = df_model["doc_prob"].apply(parse_doc_prob)
doc_prob_df = pd.DataFrame(df_model["doc_prob_parsed"].tolist(), index=df_model.index)
doc_prob_df.columns = ["doc_prob1", "doc_prob2", "doc_prob3", "doc_prob4"]
df_model = pd.concat([df_model, doc_prob_df], axis=1)

print("Target distribution:\n", df_model["progress_status"].value_counts())

# Define features and target
features = [
    "Labour_seats", 
    "Conservative_seats", 
    "LibDem_seats", 
    "sponsor_party", 
    "doc_prob1", "doc_prob2", "doc_prob3", "doc_prob4"
]
target = "progress_status"

X = df_model[features]
y = df_model[target]

# One-hot encode the categorical sponsor_party feature
X_encoded = pd.get_dummies(X, columns=["sponsor_party"], drop_first=True)

# Split into training and test sets (80%/20%)
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Train the Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=32)
model.fit(X_train, y_train)

# Predict probabilities on the test set
y_prob_test = model.predict_proba(X_test)

# Get probability for class 2 (assumed to be the positive outcome)
class_idx = list(model.classes_).index(2)
prob_class2 = y_prob_test[:, class_idx]

# Retrieve the corresponding bill_id values from the test set
test_ids = df_model.loc[X_test.index, "bill_id"]

# Create a results DataFrame and save to CSV
results_df = pd.DataFrame({
    "bill_id": test_ids,
    "RF_Probability": prob_class2
})
results_df.to_csv("predictions_rf.csv", index=False)
print("\nPredictions saved to 'predictions_rf.csv'.")

# Optionally, print performance metrics
y_pred_test = model.predict(X_test)
print("\nTest Accuracy: {:.2f}%".format(accuracy_score(y_test, y_pred_test) * 100))
try:
    ll = log_loss(y_test, y_prob_test)
except Exception:
    ll = np.nan
print("Test Log Loss: {:.4f}".format(ll))
print("\nClassification Report (Test Data):\n", classification_report(y_test, y_pred_test))
