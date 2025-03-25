import pandas as pd
import numpy as np
import ast
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, log_loss, classification_report

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.width', 1000)

df = pd.read_csv("bills_data.csv")

print("Columns in CSV:", df.columns.tolist())
print(df.head())

def parse_seat_counts(val):
    if pd.isnull(val):
        return {}
    try:
        return ast.literal_eval(val)
    except Exception as e:
        return {}

df["seat_counts_parsed"] = df["seat_counts"].apply(parse_seat_counts)

df["Labour_seats"] = df["seat_counts_parsed"].apply(lambda d: d.get("Labour", 0))
df["Conservative_seats"] = df["seat_counts_parsed"].apply(lambda d: d.get("Conservative", 0))
df["LibDem_seats"] = df["seat_counts_parsed"].apply(lambda d: d.get("Liberal Democrat", 0))

df_model = df[df["progress_status"].isin([1, 2])].copy()

print("Target distribution:\n", df_model["progress_status"].value_counts())

features = ["Labour_seats", "Conservative_seats", "LibDem_seats", "sponsor_party"]
target = "progress_status"

X = df_model[features]
y = df_model[target]

X_encoded = pd.get_dummies(X, columns=["sponsor_party"], drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print("\nTraining Accuracy: {:.2f}%".format(train_acc * 100))
print("Test Accuracy: {:.2f}%".format(test_acc * 100))

y_prob_test = model.predict_proba(X_test)
try:
    ll = log_loss(y_test, y_prob_test)
except Exception as e:
    ll = np.nan
print("Test Log Loss: {:.4f}".format(ll))
print("\nClassification Report (Test Data):\n", classification_report(y_test, y_pred_test))

test_results = X_test.copy()
test_results["True_Label"] = y_test.values
test_results["Predicted_Label"] = y_pred_test

test_results["Prediction_Correct"] = test_results.apply(
    lambda row: "True" if row["True_Label"] == row["Predicted_Label"] else "False", axis=1
)

output_filename = "test_predictions.csv"
test_results.to_csv(output_filename, index=False)
print(f"\nTest predictions have been saved to '{output_filename}'.")

correct_preds = test_results[test_results["Prediction_Correct"] == "True"]
incorrect_preds = test_results[test_results["Prediction_Correct"] == "False"]

print("\n--- 3 Sample Correct Predictions ---")
if not correct_preds.empty:
    print(correct_preds.head(3).to_string())
else:
    print("No correct predictions found.")

print("\n--- 3 Sample Incorrect Predictions ---")
if not incorrect_preds.empty:
    print(incorrect_preds.head(3).to_string())
else:
    print("No incorrect predictions found.")
