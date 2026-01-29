import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
import sys
import csv

#STEP 3 of processing
#Create tfidf matrices for each speech, parliament party, parliament member and year

clean_file = "parliament-search/public/clean.csv"
stopwords_file = 'parliament-search/public/dictionary/stopwords_stemmed.txt'
csv.field_size_limit(sys.maxsize)

def save_model_files(vectorizer, matrix, name_suffix):
    # Ensure directory exists
    model_dir = 'parliament-search/public/search_models'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    joblib.dump(vectorizer, f'{model_dir}/tfidf_vectorizer_{name_suffix}.joblib')
    joblib.dump(matrix, f'{model_dir}/tfidf_matrix_{name_suffix}.joblib')
    print(f"Models saved in '{model_dir}' with suffix: _{name_suffix}")

def analyze_group_keywords(csv_path, group_col, entity_name=None, top_n=20):
 
    print(f"\n--- Analysis: Keywords by {group_col} ---")
    
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

    # Date Processing for grouping by year
    if 'sitting_date' in df.columns:
        df['sitting_date'] = pd.to_datetime(df['sitting_date'], dayfirst=True, errors='coerce')
        # Only drop if date is missing AND we are grouping by year
        if group_col == 'year':
            df = df.dropna(subset=['sitting_date'])
            df['year'] = df['sitting_date'].dt.year.astype(int)

    # Grouping
    print(f"Grouping texts by {group_col}...")
    
    if group_col != 'speech':
        # Group by column and join speeches
        grouped_df = df.groupby(group_col)['speech'].apply(lambda x: ' '.join(x)).reset_index()
        print(f"Created {len(grouped_df)} unique groups.")
    else:
        # If grouping by speech, use the dataframe as is
        grouped_df = df.reset_index(drop=True)

    # TF-IDF Calculation
    print("Calculating TF-IDF...")

    tfidf = TfidfVectorizer() 
    tfidf_matrix = tfidf.fit_transform(grouped_df['speech'])
    feature_names = tfidf.get_feature_names_out()

    # Save the Model (Vectorizer + Matrix)
    save_model_files(tfidf, tfidf_matrix, group_col)

    # Extract Keywords & Save Results to CSV
    print("Extracting keywords and saving report...")
    
    results_data = [] 
    
    # Ensure output directory exists
    csv_dir = 'parliament-search/public/search_models_csv'
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    counter = 0
    
    for i in range(tfidf_matrix.shape[0]):
        
        if group_col == 'speech':
            entity = i 
        else:
            entity = grouped_df.iloc[i][group_col]

        row = tfidf_matrix[i]
        
        indices = row.indices
        data = row.data
        
        sorted_items = sorted(zip(indices, data), key=lambda x: x[1], reverse=True)[:top_n]
        
        top_words = [feature_names[idx] for idx, score in sorted_items]
        top_words_str = ", ".join(top_words)

        results_data.append({
            group_col: entity,
            'top_keywords': top_words_str
        })

        # Print logic for terminal feedback
        if entity_name and str(entity) == str(entity_name):
            print(f"\n>> Top keywords for {entity}:")
            print(top_words_str)
        elif not entity_name and counter < 5: 
            print(f"\n>> Top keywords for {group_col} {entity}:")
            print(top_words_str)
            counter += 1
        
        if i % 1000 == 0 and i > 0:
            print(f"Processed {i} items...", end='\r')

    # Create DataFrame and Save
    results_df = pd.DataFrame(results_data)
    
    output_filename = f"{csv_dir}/results_keywords_by_{group_col}.csv"
    results_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\nSuccess! Results saved to '{output_filename}'")
    return tfidf_matrix

# Run analyses
analyze_group_keywords(clean_file, 'speech')
analyze_group_keywords(clean_file, 'political_party')
analyze_group_keywords(clean_file, 'year')
analyze_group_keywords(clean_file, 'member_name')