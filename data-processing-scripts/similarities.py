import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

#STEP 4 of processing
#Find the pairs of parliament members with the largest similarity

def find_top_k_similar_members(clean_csv_path, k=10):
    print(f"--- Εύρεση Top-{k} Ζευγών Ομοιότητας Μελών ---")
    try:
        tfidf_matrix = joblib.load('parliament-search/public/search_models/tfidf_matrix_member_name.joblib')
        print("Ο πίνακας TF-IDF φορτώθηκε επιτυχώς.")
    except FileNotFoundError:
        print("Σφάλμα: Δεν βρέθηκε το μοντέλο. Τρέξε πρώτα το analyze_group_keywords για 'member_name'.")
        return

    print("Ανάκτηση ονομάτων μελών...")
    df = pd.read_csv(clean_csv_path)
    df = df.dropna(subset=['speech'])
    df['speech'] = df['speech'].astype(str)
    
    grouped_df = df.groupby('member_name')['speech'].apply(lambda x: ' '.join(x)).reset_index()
    member_names = grouped_df['member_name'].tolist()
    
    if len(member_names) != tfidf_matrix.shape[0]:
        print(f"Προσοχή! Ασυμφωνία μεγέθους: {len(member_names)} ονόματα vs {tfidf_matrix.shape[0]} γραμμές πίνακα.")
        return

    # Cosine Similarity
    print("Υπολογισμός πίνακα ομοιότητας...")
    sim_matrix = cosine_similarity(tfidf_matrix)

    # Top-K Pairs
    pairs = []
    num_members = len(member_names)
    
    print(f"Σάρωση {num_members} μελών για ζεύγη...")
    
    rows, cols = np.triu_indices(num_members, k=1)
    
    for i, j in zip(rows, cols):
        score = sim_matrix[i, j]
        #Only keep pairs with a similarity > 0.1
        if score > 0.1: 
            pairs.append((score, member_names[i], member_names[j]))

    pairs.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\nTop {k} Ζεύγη με τη Μεγαλύτερη Ομοιότητα")
    for i in range(min(k, len(pairs))):
        score, name1, name2 = pairs[i]
        print(f"{i+1}. {name1} <--> {name2} : {score:.4f}")

    # Save to CSV
    df_pairs = pd.DataFrame(pairs[:100], columns=['Similarity', 'Member A', 'Member B']) # Σώζουμε τα top 100
    df_pairs.to_csv('parliament-search/public/similarity/top_similar_members.csv', index=False, encoding='utf-8-sig')
    print("\nΤα top-100 ζεύγη αποθηκεύτηκαν στο 'top_similar_members.csv'")


input_file = "parliament-search/public/clean.csv"  
find_top_k_similar_members(input_file, k=10) #k=10 is the number pairs printed in the terminal