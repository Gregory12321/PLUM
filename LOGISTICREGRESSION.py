import pandas as pd
import numpy as np
import ast
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss, classification_report

# Set display options for debugging/visibility
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1000)

# Load the Excel file (assumes a "bill_id" column exists)
df = pd.read_excel("data_with_status_doc_prob.xlsx")
print("Columns in Excel:", df.columns.tolist())
print(df.head())

# Parse seat_counts
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

# Filter rows for modeling (progress_status 1 or 2)
df_model = df[df["progress_status"].isin([1, 2])].copy()

# Parse the doc_prob column
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

# Define features and target variable
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

# One-hot encode the categorical 'sponsor_party' feature
X_encoded = pd.get_dummies(X, columns=["sponsor_party"], drop_first=True)

# Split data for evaluation (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Train the Logistic Regression model with elasticnet penalty
model = LogisticRegression(penalty='elasticnet', solver='saga', l1_ratio=0.0, random_state=42, max_iter=1000)
model.fit(X_train, y_train)

# Evaluate on training and test sets
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)
print("\nTraining Accuracy: {:.2f}%".format(accuracy_score(y_train, y_pred_train) * 100))
print("Test Accuracy: {:.2f}%".format(accuracy_score(y_test, y_pred_test) * 100))
y_prob_test = model.predict_proba(X_test)
try:
    ll = log_loss(y_test, y_prob_test)
except Exception:
    ll = np.nan
print("Test Log Loss: {:.4f}".format(ll))
print("\nClassification Report (Test Data):\n", classification_report(y_test, y_pred_test))

# Generate predictions for the entire dataset
y_prob_all = model.predict_proba(X_encoded)
# Get the probability for class 2 (assumed positive)
class_idx = list(model.classes_).index(2)
all_prob = y_prob_all[:, class_idx]

# Build results DataFrame with bill_id and predictions
results_df = pd.DataFrame({
    "bill_id": df_model["bill_id"],
    "LogReg_Probability": all_prob
})
# Remove duplicate bill_id entries
results_df = results_df.drop_duplicates(subset="bill_id", keep="first")
results_df.to_csv("predictions_lr.csv", index=False)
print("\nPredictions for all bills saved to 'predictions_lr.csv'.")
