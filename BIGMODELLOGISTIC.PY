import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

def parse_doc_probs(val):
    """
    Parse the string representation of an array from the doc_probs column
    and return the last element as a float.
    """
    # Remove square brackets and any extra whitespace
    val = val.strip("[]").strip()
    # Split by whitespace (assumes numbers are space-separated)
    parts = val.split()
    # Convert each part to a float
    numbers = [float(x) for x in parts]
    # Return the last element (assumed to be the positive class probability)
    return numbers[-1]

# 1. Load the training and validation files
train_df = pd.read_excel("merged_probabilities_training_with_status.xlsx")
valid_df = pd.read_excel("validation_probabilities_training_with_status.xlsx")

# 2. Process the doc_probs column if needed: convert string to float
# Check if the first element is a string that starts with '[' to decide if parsing is necessary
if isinstance(train_df['doc_probs'].iloc[0], str) and train_df['doc_probs'].iloc[0].startswith('['):
    train_df['doc_probs'] = train_df['doc_probs'].apply(parse_doc_probs)
    
if isinstance(valid_df['doc_probs'].iloc[0], str) and valid_df['doc_probs'].iloc[0].startswith('['):
    valid_df['doc_probs'] = valid_df['doc_probs'].apply(parse_doc_probs)

# 3. Identify feature columns
# We'll use all columns except for 'bill_id' and 'status'
features = [col for col in train_df.columns if col not in ['bill_id', 'status']]
print("Using features:", features)

# 4. Prepare training and validation datasets
X_train = train_df[features]
y_train = train_df['status']

X_valid = valid_df[features]
y_valid = valid_df['status']

# 5. Train the logistic regression model
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

# 6. Get predictions for training and validation sets
train_preds = clf.predict(X_train)
valid_preds = clf.predict(X_valid)

# 7. Calculate accuracy percentages
train_accuracy = accuracy_score(y_train, train_preds) * 100
valid_accuracy = accuracy_score(y_valid, valid_preds) * 100

print(f"Training Accuracy: {train_accuracy:.2f}%")
print(f"Validation Accuracy: {valid_accuracy:.2f}%")
