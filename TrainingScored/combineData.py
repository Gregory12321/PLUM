import pandas as pd
import glob

# 1. Load the main Excel file
df_main = pd.read_excel("data.xlsx")

# 2. Load all CSV files in the folder "CSVFilesWithTitleScores" that end with _withTitleScores.csv
csv_files = glob.glob("CSVFilesWithTitleScores/*withTitleScores.csv")
csv_list = [pd.read_csv(csv_file) for csv_file in csv_files]

# 3. Concatenate the CSV files into one DataFrame
df_csv = pd.concat(csv_list, ignore_index=True)

# 4. Standardize the column names for merging
#    We want the "Bill Id" from CSV to match "bill_id" from Excel.
#    Also, we rename "Status" and "doc_probs" to a simpler name if needed.
df_csv.rename(columns={
    'Bill Id': 'bill_id',
    'Status': 'status',
    'doc_probs': 'doc_prob'
}, inplace=True)

# 5. Merge the Excel DataFrame with the CSV DataFrame on the 'bill_id' column.
#    This is a left join, so every row in df_main is preserved.
df_merged = pd.merge(df_main, df_csv[['bill_id', 'status', 'doc_prob']], on='bill_id', how='left')

# 6. Write the updated DataFrame to a new Excel file
df_merged.to_excel("data_with_status_doc_prob.xlsx", index=False)
