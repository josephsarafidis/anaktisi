import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def find_top_k_similar_members(clean_csv_path, k=10):
    print(f"--- Εύρεση Top-{k} Ζευγών Ομοιότητας Μελών ---")
    
    # 1. Φόρτωση του έτοιμου Πίνακα TF-IDF για τα μέλη
    # Προϋπόθεση: Να έχει τρέξει ήδη το analyze_group_keywords(..., 'member_name')
    try:
        tfidf_matrix = joblib.load('search_models/tfidf_matrix_member_name.joblib')
        print("Ο πίνακας TF-IDF φορτώθηκε επιτυχώς.")
    except FileNotFoundError:
        print("Σφάλμα: Δεν βρέθηκε το μοντέλο. Τρέξε πρώτα το analyze_group_keywords για 'member_name'.")
        return

    # 2. Ανάκτηση των Ονομάτων (για να ξέρουμε ποιος είναι ποιος)
    # Πρέπει να κάνουμε το ίδιο groupby για να έχουμε την ίδια σειρά με τον πίνακα
    print("Ανάκτηση ονομάτων μελών...")
    df = pd.read_csv(clean_csv_path)
    df = df.dropna(subset=['speech'])
    df['speech'] = df['speech'].astype(str)
    
    # Ομαδοποίηση (ακριβώς όπως στο προηγούμενο βήμα) για να πάρουμε τα ονόματα στη σωστή σειρά
    grouped_df = df.groupby('member_name')['speech'].apply(lambda x: ' '.join(x)).reset_index()
    member_names = grouped_df['member_name'].tolist()
    
    # Έλεγχος αν ο αριθμός των ονομάτων ταιριάζει με τις γραμμές του πίνακα
    if len(member_names) != tfidf_matrix.shape[0]:
        print(f"Προσοχή! Ασυμφωνία μεγέθους: {len(member_names)} ονόματα vs {tfidf_matrix.shape[0]} γραμμές πίνακα.")
        return

    # 3. Υπολογισμός Ομοιότητας (Cosine Similarity)
    # Αυτό δημιουργεί έναν τετραγωνικό πίνακα όπου η θέση [i, j] είναι η ομοιότητα του μέλους i με το j
    print("Υπολογισμός πίνακα ομοιότητας...")
    sim_matrix = cosine_similarity(tfidf_matrix)

    # 4. Εύρεση των Top-K ζευγών
    # Διατρέχουμε μόνο το άνω τρίγωνο του πίνακα για να αποφύγουμε διπλότυπα (A-B και B-A) και τον εαυτό τους (A-A)
    pairs = []
    num_members = len(member_names)
    
    print(f"Σάρωση {num_members} μελών για ζεύγη...")
    
    # Χρησιμοποιούμε numpy για ταχύτητα: παίρνουμε τους δείκτες του άνω τριγώνου (χωρίς τη διαγώνιο k=1)
    # Η triu_indices επιστρέφει δύο πίνακες: row_indices και col_indices
    rows, cols = np.triu_indices(num_members, k=1)
    
    
    # Για κάθε ζεύγος δεικτών, αποθηκεύουμε (score, όνομα1, όνομα2)
    for i, j in zip(rows, cols):
        score = sim_matrix[i, j]
        # Κρατάμε μόνο ζεύγη με κάποια σχετική ομοιότητα (π.χ. > 0.1) για να μην γεμίζουμε τη μνήμη αν είναι τεράστιο
        if score > 0.1: 
            pairs.append((score, member_names[i], member_names[j]))

    # 5. Ταξινόμηση και Εκτύπωση
    # Ταξινομούμε φθίνουσα (reverse=True) με βάση το score (το πρώτο στοιχείο του tuple)
    pairs.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\nTop {k} Ζεύγη με τη Μεγαλύτερη Ομοιότητα")
    for i in range(min(k, len(pairs))):
        score, name1, name2 = pairs[i]
        print(f"{i+1}. {name1} <--> {name2} : {score:.4f}")

    # Προαιρετικά: Αποθήκευση σε CSV
    df_pairs = pd.DataFrame(pairs[:100], columns=['Similarity', 'Member A', 'Member B']) # Σώζουμε τα top 100
    df_pairs.to_csv('similarity/top_similar_members.csv', index=False, encoding='utf-8-sig')
    print("\nΤα top-100 ζεύγη αποθηκεύτηκαν στο 'top_similar_members.csv'")


input_file = "data/clean.csv"  # Ή το αρχείο που χρησιμοποίησες για το grouping
find_top_k_similar_members(input_file, k=10)