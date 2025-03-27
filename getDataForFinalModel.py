import pandas as pd

# 1. Load the merged probabilities file
df_merged = pd.read_excel("merged_probabilities.xlsx")

# 2. Define the file paths with corresponding split types
files_info = [
    {"path": "fullTextProbabilities/18/Training/training_text18.csv", "split": "training"},
    {"path": "fullTextProbabilities/19/Training/training_text19.csv", "split": "training"},
    {"path": "fullTextProbabilities/28/Training/training_text28.csv", "split": "training"},
    {"path": "fullTextProbabilities/29/Training/training_text29.csv", "split": "training"},
    {"path": "fullTextProbabilities/18/Validation/validation_text18.csv", "split": "validation"},
    {"path": "fullTextProbabilities/19/Validation/validation_text19.csv", "split": "validation"},
    {"path": "fullTextProbabilities/28/Validation/validation_text28.csv", "split": "validation"},
    {"path": "fullTextProbabilities/29/Validation/validation_text29.csv", "split": "validation"}
]

# 3. Load each CSV, add a split column, and combine them
csv_dfs = []
for info in files_info:
    df = pd.read_csv(info["path"])
    df["split"] = info["split"]
    csv_dfs.append(df)

# Combine all CSV files into one dataframe
df_all = pd.concat(csv_dfs, ignore_index=True)

# 4. Merge the probabilities file with the combined CSV file
# We assume "bill_id" in df_merged corresponds to "id" in df_all.
df_merged_full = pd.merge(df_merged, df_all[['id', 'doc_probs', 'split']],
                          left_on='bill_id', right_on='id', how='left')

# Optionally remove the extra "id" column from df_all
df_merged_full.drop(columns=['id'], inplace=True)

# 5. Split the merged dataframe into training and validation
df_training = df_merged_full[df_merged_full['split'] == 'training'].copy()
df_validation = df_merged_full[df_merged_full['split'] == 'validation'].copy()

# Optionally drop the "split" column if no longer needed
df_training.drop(columns=['split'], inplace=True)
df_validation.drop(columns=['split'], inplace=True)

# 6. Save the resulting dataframes to Excel files
df_training.to_excel("merged_probabilities_training.xlsx", index=False)
df_validation.to_excel("validation_probabilities_training.xlsx", index=False)

print("Files created: merged_probabilities_training.xlsx and validation_probabilities_training.xlsx")
