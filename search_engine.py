import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- ΡΥΘΜΙΣΕΙΣ ---
# Εδώ βάλε τα σωστά μονοπάτια που έχεις στον υπολογιστή σου
PATHS = {
    'vectorizer': 'search_models/tfidf_vectorizer_speech.joblib', # Το αρχείο που έσωσες στο βήμα του TF-IDF
    'matrix': 'search_models/tfidf_matrix_speech.joblib',         # Ο πίνακας που έσωσες
    'data': 'data/clean.csv'                                      # Τα αρχικά δεδομένα για να δείχνουμε κείμενο/όνομα
}

class SearchEngine:
    def __init__(self):
        print("Φόρτωση της μηχανής αναζήτησης (μπορεί να πάρει λίγο)...")
        
        # 1. Φόρτωση Vectorizer και Matrix (τα φορτώνουμε στη μνήμη μια φορά)
        try:
            self.vectorizer = joblib.load(PATHS['vectorizer'])
            self.tfidf_matrix = joblib.load(PATHS['matrix'])
            
            # 2. Φόρτωση των δεδομένων (για να επιστρέφουμε ονόματα και κείμενα)
            # Φορτώνουμε μόνο τις στήλες που θέλουμε για να γλιτώσουμε μνήμη
            self.df = pd.read_csv(PATHS['data'], usecols=['member_name', 'sitting_date', 'speech', 'political_party'])
            
            # Βεβαιωνόμαστε ότι τα index ταιριάζουν (αν έκανες dropna στο training)
            self.df = self.df.dropna(subset=['speech'])
            self.df['speech'] = self.df['speech'].astype(str)
            # Αν στο training πέταξες τα μικρά κείμενα, πρέπει να κάνεις το ίδιο κι εδώ
            self.df = self.df[self.df['speech'].str.len() >= 50].reset_index(drop=True)
            
            print("Η μηχανή αναζήτησης είναι έτοιμη!")
            
        except FileNotFoundError as e:
            print(f"Σφάλμα: Δεν βρέθηκε κάποιο αρχείο. {e}")
            self.vectorizer = None

    def search(self, user_query, top_n=10):
        """
        Αυτή είναι η συνάρτηση που θα καλεί η ιστοσελίδα.
        """
        if not self.vectorizer:
            return [{"error": "Models not loaded"}]

        # 1. Μετατροπή του query σε διάνυσμα (χρησιμοποιώντας το ήδη εκπαιδευμένο vectorizer)
        # ΠΡΟΣΟΧΗ: Χρησιμοποιούμε .transform(), ΟΧΙ .fit_transform()
        query_vec = self.vectorizer.transform([user_query])

        # 2. Υπολογισμός Ομοιότητας (Cosine Similarity)
        # Συγκρίνουμε το query με ΟΛΕΣ τις ομιλίες
        similarity_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 3. Ταξινόμηση (Sort)
        # Παίρνουμε τα indices των top_n αποτελεσμάτων (με φθίνουσα σειρά score)
        top_indices = similarity_scores.argsort()[::-1][:top_n]
        
        results = []
        for idx in top_indices:
            score = similarity_scores[idx]
            
            # Αν το σκορ είναι 0, σημαίνει ότι δεν βρέθηκε καμία κοινή λέξη
            if score == 0:
                continue
                
            # Ανάκτηση πληροφοριών από το DataFrame
            row = self.df.iloc[idx]
            
            # Κόβουμε το κείμενο για preview (π.χ. τους πρώτους 200 χαρακτήρες)
            preview_text = row['speech'][:200] + "..." if len(row['speech']) > 200 else row['speech']

            result_item = {
                'score': round(float(score), 4),  # Πόσο ταιριάζει (0 έως 1)
                'member_name': row['member_name'],
                'date': row['sitting_date'],
                'party': row.get('political_party', 'N/A'),
                'preview': preview_text,
                'full_text': row['speech'] # Αν θες να το δείξεις όλο σε modal
            }
            results.append(result_item)

        return results

# --- ΠΩΣ ΤΟ ΧΡΗΣΙΜΟΠΟΙΕΙ Ο ΜΠΡΟ ΣΤΟ BACKEND ---

    # Αυτό τρέχει μόνο αν ανοίξεις το αρχείο για δοκιμή
    
# 1. Αρχικοποίηση (γίνεται μια φορά όταν ξεκινάει ο server)
engine = SearchEngine()

# 2. Αναζήτηση (αυτό έρχεται από το input του χρήστη)
query = "μνημονιο"

print(f"\nΑποτελέσματα για: '{query}'\n")
results = engine.search(query, top_n=5)

for res in results:
    print(f"[{res['score']}] {res['member_name']} ({res['date']})")
    print(f"   {res['preview']}\n")