import pandas as pd
import random

INPUT_FILE = "3A2M.csv"
OUTPUT_FILE = "recipes_sampled_1500_per_genre.csv"
CHUNK_SIZE = 50000

GENRES = [
    "bakery", "drinks", "nonveg", "vegetables",
    "fastfood", "cereal", "meal", "sides", "fusion"
]

SAMPLES_PER_GENRE = 1500

# Store collected samples
genre_samples = {g: [] for g in GENRES}

# Track counts safely
genre_counts = {g: 0 for g in GENRES}

for chunk in pd.read_csv(INPUT_FILE, chunksize=CHUNK_SIZE):
    
    for genre in GENRES:
        if genre_counts[genre] >= SAMPLES_PER_GENRE:
            continue
        
        subset = chunk[chunk['genre'] == genre]
        
        if not subset.empty:
            remaining = SAMPLES_PER_GENRE - genre_counts[genre]
            
            sampled = subset.sample(
                n=min(remaining, len(subset)),
                random_state=random.randint(1, 10000)
            )
            
            genre_samples[genre].append(sampled)
            genre_counts[genre] += len(sampled)

    # Safe stopping condition (no concat)
    if all(genre_counts[g] >= SAMPLES_PER_GENRE for g in GENRES):
        break


# Combine all results
final_list = []

for g in GENRES:
    if genre_samples[g]:  # avoid empty
        final_list.append(pd.concat(genre_samples[g]))

final_df = pd.concat(final_list)

# Shuffle
final_df = final_df.sample(frac=1).reset_index(drop=True)

# Save
final_df.to_csv(OUTPUT_FILE, index=False)

print("Done!")
print("Rows per genre:", genre_counts)
print("Total rows:", len(final_df))