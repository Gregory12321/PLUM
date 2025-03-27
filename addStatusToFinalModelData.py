import pandas as pd

# 1. Load the status file which has 'bill_id' and 'status'
df_status = pd.read_excel("data_with_status_doc_prob.xlsx", usecols=["bill_id", "status"])

# 2. Process the training file
# Load the training probabilities file
df_training = pd.read_excel("merged_probabilities_training.xlsx")
# Merge on 'bill_id' to add the 'status' column
df_training_status = pd.merge(df_training, df_status, on="bill_id", how="left")
# Save the updated training file with status
df_training_status.to_excel("merged_probabilities_training_with_status.xlsx", index=False)

# 3. Process the validation file
# Load the validation probabilities file
df_validation = pd.read_excel("validation_probabilities_training.xlsx")
# Merge on 'bill_id' to add the 'status' column
df_validation_status = pd.merge(df_validation, df_status, on="bill_id", how="left")
# Save the updated validation file with status
df_validation_status.to_excel("validation_probabilities_training_with_status.xlsx", index=False)

print("Updated files created: merged_probabilities_training_with_status.xlsx and validation_probabilities_training_with_status.xlsx")
