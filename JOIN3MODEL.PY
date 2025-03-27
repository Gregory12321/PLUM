import pandas as pd

# Read each CSV file (each has bill_id and its model’s probability)
df_rf = pd.read_csv("predictions_rf.csv")
df_lr = pd.read_csv("predictions_lr.csv")
df_gb = pd.read_csv("predictions_gb.csv")

# Merge on bill_id
merged_df = pd.merge(df_rf, df_lr, on="bill_id", how="outer")
merged_df = pd.merge(merged_df, df_gb, on="bill_id", how="outer")

# Save the merged DataFrame to a new Excel file
merged_df.to_excel("merged_probabilities.xlsx", index=False)
print("Merged probabilities saved to 'merged_probabilities.xlsx'")
