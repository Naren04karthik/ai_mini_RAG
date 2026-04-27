import pandas as pd

# Load dataset
df = pd.read_csv("recipes_sampled_1500_per_genre.csv")

# Drop specific columns
df = df.drop(columns=["Unnamed: 0", "label"], errors='ignore')

# Save cleaned dataset
df.to_csv("recipes_cleaned.csv", index=False)

print("Cleaned dataset saved as recipes_cleaned.csv")
print("Remaining columns:", df.columns.tolist())