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
    if not os.path.exists('search_models'):
        os.makedirs('search_models')
    
    joblib.dump(vectorizer, f'parliament-search/public/search_models/tfidf_vectorizer_{name_suffix}.joblib')
    joblib.dump(matrix, f'parliament-search/public/search_models/tfidf_matrix_{name_suffix}.joblib')
    print(f"Models saved in 'search_models' with suffix: _{name_suffix}")

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
        df = df.dropna(subset=['sitting_date'])
        df['year'] = df['sitting_date'].dt.year.astype(int)

    # Grouping
    print(f"Grouping texts by {group_col}...")
    # Join all speeches of a group into one massive string
    if group_col != 'speech':
        grouped_df = df.groupby(group_col)['speech'].apply(lambda x: ' '.join(x)).reset_index()
        print(f"Created {len(grouped_df)} unique groups.")
    else:
        grouped_df = df
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
    dense = tfidf_matrix.todense()
    counter = 0
    for i, (idx, row) in enumerate(grouped_df.iterrows()):
        entity = row[group_col]
        episode_vector = dense[i].tolist()[0]
        phrase_scores = [pair for pair in zip(feature_names, episode_vector) if pair[1] > 0]
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
    
    # Save to CSV 
    output_filename = f"parliament-search/public/search_models_csv/results_keywords_by_{group_col}.csv"
    results_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\nSuccess! Results saved to '{output_filename}'")
    return tfidf_matrix



analyze_group_keywords(clean_file, 'speech')
analyze_group_keywords(clean_file, 'political_party')
analyze_group_keywords(clean_file, 'year')
analyze_group_keywords(clean_file, 'member_name')


#OPTIONAL - To see results for a specific entity in the terminal follow this example:
# analyze_group_keywords(clean_file, 'political_party', entity_name='ΝΕΑ ΔΗΜΟΚΡΑΤΙΑ')