import pandas as pd
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from greek_stemmer import stemmer
import re  
import string


# Αρχικοποίηση του App
app = FastAPI()

# --- ΡΥΘΜΙΣΗ CORS (Πολύ σημαντικό για το JSX Frontend) ---
origins = [
    "http://localhost:5173"  # Αν χρησιμοποιείς Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ΦΟΡΤΩΣΗ ΜΟΝΤΕΛΩΝ ΚΑΙ ΔΕΔΟΜΕΝΩΝ ---
# Εδώ θα πρέπει να φορτώσεις τα αρχεία που έχεις σώσει
# Αν δεν τα έχεις σώσει ακόμα, πες μου να σου πω πώς!
try:
    tfidf_vectorizer = joblib.load('../public/search_models/tfidf_vectorizer_speech.joblib') 
    tfidf_matrix = joblib.load('../public/search_models/tfidf_matrix_speech.joblib') 
    df = pd.read_csv('../public/clean_full_speeches.csv').fillna('')
    
    # === ΝΕΟ: Δημιουργία στήλης Year κατά τη φόρτωση ===
    # Μετατρέπουμε το sitting_date σε datetime και βγάζουμε το έτος
    # Υποθέτουμε ότι το date format είναι dd/mm/yyyy
    print("Processing dates...")
    df['date_obj'] = pd.to_datetime(df['sitting_date'], format='%d/%m/%Y', errors='coerce')
    df['year'] = df['date_obj'].dt.year.fillna(0).astype(int)
    
    print("Models and Data loaded successfully!")
except Exception as e:
    print(f"Error loading: {e}")
    df = pd.DataFrame()
    tfidf_matrix = None
    tfidf_vectorizer = None

# ... (η preprocess_query παραμένει ίδια)

# --- ΝΕΟ REQUEST MODEL ---
class TrendQuery(BaseModel):
    word: str

# --- ΝΕΟ ENDPOINT ΓΙΑ ΤΟ ΓΡΑΦΗΜΑ ---
@app.post("/trend")
def get_word_trend(req: TrendQuery):
    if tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    # 1. Καθαρίζουμε τη λέξη όπως στο search
    processed_word = preprocess_query(req.word)
    
    # Αν μετά το καθάρισμα δεν έμεινε τίποτα (π.χ. ήταν stopword)
    if not processed_word:
        return {"data": []}

    # Επειδή το processed_word μπορεί να είναι πολλές λέξεις αν έγραψε πρόταση,
    # παίρνουμε την πρώτη ή κάνουμε loop. Ας υποθέσουμε ότι ψάχνει ΜΙΑ λέξη για trend.
    target_token = processed_word.split()[0] if " " in processed_word else processed_word

    # 2. Βρίσκουμε το index της λέξης στο λεξιλόγιο (Vocabulary)
    if target_token not in tfidf_vectorizer.vocabulary_:
        return {"data": [], "message": "Word not found in vocabulary"}
    
    word_index = tfidf_vectorizer.vocabulary_[target_token]

    # 3. Παίρνουμε ολόκληρη τη στήλη για αυτή τη λέξη από τον πίνακα TF-IDF
    # Αυτό μας δίνει το score της λέξης για ΚΑΘΕ ομιλία (sparse column)
    word_scores = tfidf_matrix[:, word_index].toarray().flatten()

    # 4. Φτιάχνουμε ένα προσωρινό DataFrame για να κάνουμε το GroupBy
    # Χρησιμοποιούμε μόνο τα μη μηδενικά για ταχύτητα, αλλά εδώ το κάνουμε απλά:
    temp_df = pd.DataFrame({
        'year': df['year'],
        'score': word_scores
    })

    # 5. Ομαδοποίηση ανά έτος και άθροισμα (ή mean)
    # Το sum δείχνει τη συνολική χρήση/σημασία της λέξης εκείνη τη χρονιά
    trend_data = temp_df[temp_df['year'] > 0].groupby('year')['score'].sum().reset_index()
    
    # Ταξινόμηση ανά έτος
    trend_data = trend_data.sort_values('year')

    # 6. Ετοιμασία JSON για το React
    result = trend_data.to_dict(orient='records') # [{'year': 1989, 'score': 1.5}, ...]
    
    return {"data": result, "token": target_token}

# --- ΤΟ ΜΟΝΤΕΛΟ ΤΟΥ REQUEST ---
class SearchQuery(BaseModel):
    query: str
    top_k: int = 10  # Default επιστροφή 5 αποτελεσμάτων

# --- ΣΥΝΑΡΤΗΣΗ PREPROCESSING ---

def load_stopwords(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
        return set()


translator = str.maketrans(string.punctuation + '΄‘’“”«»…–', ' ' * (len(string.punctuation) + 9))

digit_punct_cleaner = re.compile(r'(?<=\d)[\.,](?=\d)')

digit_punct_cleaner = re.compile(r'(?<=\d)[\.,](?=\d)') 

STOPWORDS_FILE = '../public/dictionary/stopwords_stemmed.txt'

stopwords = load_stopwords(STOPWORDS_FILE)


def preprocess_query(text):
  
    # 1. Lowercase and Remove specific number formatting like 1.000
    text = digit_punct_cleaner.sub('', text.lower())
    
    # 2. Remove Punctuation (Fastest method in Python)
    text = text.translate(translator)
    
    # 3. Split into words
    words = text.split()
    
    cleaned_words = []
    
    for word in words:
        if word in stopwords or len(word) < 2:
            continue
            
        stemmed_upper = stemmer.stem_word(word.upper(), 'VBG')
        
        if stemmed_upper.islower():
            continue # Skip this word
            
        stemmed_lower = stemmed_upper.lower()
        
        if stemmed_lower in stopwords:
            continue
            
        cleaned_words.append(stemmed_lower)

    return ' '.join(cleaned_words)


# --- ΤΟ ENDPOINT ---
@app.post("/search")
def search_api(req: SearchQuery):
    if tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="Models not loaded properly.")

    # Βήμα 1: Καθαρισμός του query
    processed_query = preprocess_query(req.query)
    
    # Βήμα 2: Μετατροπή σε TF-IDF vector
    # Προσοχή: Χρησιμοποιούμε transform, ΟΧΙ fit_transform
    query_vec = tfidf_vectorizer.transform([processed_query])
    
    # Βήμα 3: Υπολογισμός ομοιότητας
    # cosine_similarity επιστρέφει πίνακα (1, n_samples), θέλουμε το flatten
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Βήμα 4: Εύρεση των top-k (argsort επιστρέφει δείκτες από μικρότερο σε μεγαλύτερο)
    # Παίρνουμε τα τελευταία k και κάνουμε αναστροφή [::-1]
    top_indices = similarities.argsort()[-req.top_k:][::-1]
    
    # Βήμα 5: Εξαγωγή αποτελεσμάτων
    results = []
    for idx in top_indices:
        score = similarities[idx]
        if score > 0.05: # Φίλτρο: Αν η ομοιότητα είναι πολύ μικρή, αγνόησέ το (προαιρετικό)
            row = df.iloc[idx]
            results.append({
                "member_name": row['member_name'],
                "sitting_date": row['sitting_date'],
                "political_party": row['political_party'],
                "speech_snippet": row['speech'][:300] + "...", # Επιστρέφουμε μόνο την αρχή για preview
                "full_speech": row['speech'], # Όλη η ομιλία για να τη δείξεις στο modal/page
                "score": float(round(score, 4))
            })
    
    return {"results": results, "count": len(results)}
# Για να το τρέξεις: uvicorn main:app --reload