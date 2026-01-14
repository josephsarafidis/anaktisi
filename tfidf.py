import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
import sys
import csv

# --- Configuration ---
input_file = "data/Greek_Parliament_Proceedings_1989_2020.csv" 
clean_file = "data/clean.csv"
sample_file = "data/random_sample.csv"
stopwords_file = 'dictionary/stopwords_stemmed.txt'
csv.field_size_limit(sys.maxsize)

# --- Helper Function to Save Models ---
def save_model_files(vectorizer, matrix, name_suffix):
    """
    Saves the vectorizer and matrix to the search_models folder.
    name_suffix: e.g., 'political_party' or '2010'
    """
    if not os.path.exists('search_models'):
        os.makedirs('search_models')
    
    # Save with specific suffix
    joblib.dump(vectorizer, f'search_models/tfidf_vectorizer_{name_suffix}.joblib')
    joblib.dump(matrix, f'search_models/tfidf_matrix_{name_suffix}.joblib')
    print(f"Models saved in 'search_models' with suffix: _{name_suffix}")

# --- Main Analysis Function ---
def analyze_group_keywords(csv_path, group_col, entity_name=None, top_n=20):
 
    print(f"\n--- Analysis: Keywords by {group_col} ---")
    
    # 1. Load Data
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        return

    # Basic Cleaning
    if 'speech' not in df.columns:
        print("Error: Column 'speech' not found.")
        return

    df = df.dropna(subset=['speech'])
    df['speech'] = df['speech'].astype(str)


    # Date Processing (Only needed if grouping by year, but good to have)
    if 'sitting_date' in df.columns:
        df['sitting_date'] = pd.to_datetime(df['sitting_date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['sitting_date'])
        df['year'] = df['sitting_date'].dt.year.astype(int)

    # 2. Grouping
    print(f"Grouping texts by {group_col}...")
    # Join all speeches of a group into one massive string
    if group_col != 'speech':
        grouped_df = df.groupby(group_col)['speech'].apply(lambda x: ' '.join(x)).reset_index()
        print(f"Created {len(grouped_df)} unique groups.")
    else:
        grouped_df = df
    # 3. TF-IDF Calculation
    print("Calculating TF-IDF...")

    tfidf = TfidfVectorizer() 
    tfidf_matrix = tfidf.fit_transform(grouped_df['speech'])
    feature_names = tfidf.get_feature_names_out()
    

    # 4. Save the Model (Vectorizer + Matrix)
    save_model_files(tfidf, tfidf_matrix, group_col)

    # 5. Extract Keywords & Save Results to CSV
    print("Extracting keywords and saving report...")
    
    results_data = [] # List to store data for the CSV
    dense = tfidf_matrix.todense()
    counter = 0
    for i, (idx, row) in enumerate(grouped_df.iterrows()):
        entity = row[group_col]
        
        # Get score vector for this group
        episode_vector = dense[i].tolist()[0]
        
        # Zip words with scores
        phrase_scores = [pair for pair in zip(feature_names, episode_vector) if pair[1] > 0]
        
        # Sort by score descending
        sorted_phrases = sorted(phrase_scores, key=lambda t: t[1] * -1)
        
        # Get top N words
        top_words = [word for word, score in sorted_phrases[:top_n]]

        top_words_str = ", ".join(top_words)


        # Add to list
        if group_col == 'speech':
            results_data.append({
                group_col: i,
                'top_keywords': top_words_str
            })
        else:
            results_data.append({
                group_col: entity,
                'top_keywords': top_words_str
            })

        # Print specific entity if requested
        if entity_name and str(entity) == str(entity_name):
            print(f"\n>> Top keywords for {entity}:")
            print(top_words_str)
        elif not entity_name and counter < 20:
            print(f"\n>> Top keywords for {group_col} {i}:")
            print(top_words_str)
            counter+=1
    
    # Create DataFrame and Save
    results_df = pd.DataFrame(results_data)
    
    # Save to CSV (utf-8-sig is important for Greek characters in Excel)
    output_filename = f"search_models_csv/results_keywords_by_{group_col}.csv"
    results_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\nSuccess! Results saved to '{output_filename}'")
    return tfidf_matrix

# --- Execution ---

# Example 1: Analyze by Year (e.g., 2010 vs 2011...)
# This will save 'results_keywords_by_year.csv'



analyze_group_keywords(clean_file, 'speech')
analyze_group_keywords(clean_file, 'political_party')
analyze_group_keywords(clean_file, 'year')
analyze_group_keywords(clean_file, 'member_name')


# Example 2: Analyze by Political Party
# This will save 'results_keywords_by_political_party.csv'
# analyze_group_keywords(clean_file, 'political_party', entity_name='ΝΕΑ ΔΗΜΟΚΡΑΤΙΑ')