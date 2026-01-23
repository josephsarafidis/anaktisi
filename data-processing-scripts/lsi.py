import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import os

def perform_lsi_analysis(csv_path, n_topics=10):
    print(f"\nΈναρξη LSI Analysis (Θέματα: {n_topics})")
    
    # 1. Φόρτωση Δεδομένων
    try:
        df = pd.read_csv(csv_path)
        print("Το αρχείο φορτώθηκε επιτυχώς.")
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {csv_path} δεν βρέθηκε.")
        return

    # Έλεγχος αν υπάρχει στήλη 'speech'
    if 'speech' not in df.columns:
        print("Σφάλμα: Δεν βρέθηκε στήλη 'speech'.")
        return

    # 2. Καθαρισμός & Φίλτρο (>= 50 χαρακτήρες)
    df = df.dropna(subset=['speech'])
    df['speech'] = df['speech'].astype(str)
    
    if df.empty:
        print("Δεν έμειναν δεδομένα προς ανάλυση.")
        return

    # 3. TF-IDF (Προετοιμασία για το LSI)
    print("Υπολογισμός TF-IDF...")
    # min_df=5: Αγνοεί λέξεις που εμφανίζονται σε λιγότερες από 5 ομιλίες (καθαρίζει θόρυβο)
    tfidf = TfidfVectorizer(min_df=5) 
    tfidf_matrix = tfidf.fit_transform(df['speech'])
    feature_names = tfidf.get_feature_names_out()

    # 4. Εφαρμογή LSI (Truncated SVD)
    print(f"Εκτέλεση LSI για εντοπισμό {n_topics} θεματικών ενοτήτων...")
    
    lsi_model = TruncatedSVD(n_components=n_topics, random_state=42)
    lsi_matrix = lsi_model.fit_transform(tfidf_matrix)

    # 5. Εμφάνιση των λέξεων-κλειδιών για κάθε Θέμα (Topic)
    print("\nΟι Σημαντικότερες Λέξεις ανά Θεματική Ενότητα (Topic)")
    topic_keywords = []
    
    for i, component in enumerate(lsi_model.components_):
        # Ζευγαρώνουμε λέξεις με βάρη και ταξινομούμε
        zipped = zip(feature_names, component)
        top_terms = sorted(zipped, key=lambda t: t[1], reverse=True)[:15] # Top 15 λέξεις
        
        keywords = ", ".join([term for term, weight in top_terms])
        print(f"Topic {i+1}: {keywords}")
        topic_keywords.append(keywords)

    # 6. Αποθήκευση αποτελεσμάτων (Διανύσματα)
    print("\nΑποθήκευση διανυσμάτων σε CSV...")
    
    # Μετατροπή του πίνακα LSI σε DataFrame
    topic_cols = [f'Topic_{i+1}' for i in range(n_topics)]
    lsi_df = pd.DataFrame(lsi_matrix, columns=topic_cols)
    
    # Επαναφορά του index στο αρχικό df για να κολλήσουμε σωστά τις στήλες
    df_reset = df.reset_index(drop=True)
    
    # Ενώνουμε τα αρχικά δεδομένα με τα vectors
    final_df = pd.concat([df_reset, lsi_df], axis=1)
    
    # Δημιουργία φακέλου αν δεν υπάρχει
    os.makedirs('lsi_results', exist_ok=True)
    output_path = 'parliament-search/public/lsi_results/speech_vectors_lsi.csv'
    
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Επιτυχία! Το αρχείο αποθηκεύτηκε στο: {output_path}")
    
    # Επιστρέφουμε τον πίνακα αν θες να τον χρησιμοποιήσεις αλλού
    return lsi_matrix, lsi_model


my_csv = 'parliament-search/public/clean.csv' 
    
# Κάλεσε τη συνάρτηση (π.χ. για 10 θέματα)
vectors, model = perform_lsi_analysis(my_csv, n_topics=10)