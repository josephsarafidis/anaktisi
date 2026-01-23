import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import os

#STEP 5 of processing
#Perform LSI analysis

def perform_lsi_analysis(csv_path, n_topics=10):
    print(f"\nΈναρξη LSI Analysis (Θέματα: {n_topics})")
    
    try:
        df = pd.read_csv(csv_path)
        print("Το αρχείο φορτώθηκε επιτυχώς.")
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {csv_path} δεν βρέθηκε.")
        return

    if 'speech' not in df.columns:
        print("Σφάλμα: Δεν βρέθηκε στήλη 'speech'.")
        return

    df = df.dropna(subset=['speech'])
    df['speech'] = df['speech'].astype(str)
    
    if df.empty:
        print("Δεν έμειναν δεδομένα προς ανάλυση.")
        return

    print("Υπολογισμός TF-IDF...")
    tfidf = TfidfVectorizer(min_df=5) 
    tfidf_matrix = tfidf.fit_transform(df['speech'])
    feature_names = tfidf.get_feature_names_out()

    # LSI
    print(f"Εκτέλεση LSI για εντοπισμό {n_topics} θεματικών ενοτήτων...")
    
    lsi_model = TruncatedSVD(n_components=n_topics, random_state=42)
    lsi_matrix = lsi_model.fit_transform(tfidf_matrix)

    # Print most important keywords for each topic
    print("\nΟι Σημαντικότερες Λέξεις ανά Θεματική Ενότητα (Topic)")
    topic_keywords = []
    
    for i, component in enumerate(lsi_model.components_):
        zipped = zip(feature_names, component)
        top_terms = sorted(zipped, key=lambda t: t[1], reverse=True)[:15] # Top 15 words
        
        keywords = ", ".join([term for term, weight in top_terms])
        print(f"Topic {i+1}: {keywords}")
        topic_keywords.append(keywords)

    # Save results
    print("\nΑποθήκευση διανυσμάτων σε CSV...")
    
    topic_cols = [f'Topic_{i+1}' for i in range(n_topics)]
    lsi_df = pd.DataFrame(lsi_matrix, columns=topic_cols)
    df_reset = df.reset_index(drop=True)
    final_df = pd.concat([df_reset, lsi_df], axis=1)
    

    output_path = 'parliament-search/public/lsi_results/speech_vectors_lsi.csv'
    
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Επιτυχία! Το αρχείο αποθηκεύτηκε στο: {output_path}")
    
    return lsi_matrix, lsi_model


input_file = 'parliament-search/public/clean.csv' 
    
vectors, model = perform_lsi_analysis(input_file, n_topics=10)