import os
import re
import string
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity
from greek_stemmer import stemmer

#Python API for the web application. Implements /search and /trend

app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, '..', 'public')

print(f"DEBUG: Base Directory is {BASE_DIR}")
print(f"DEBUG: Public Directory is {PUBLIC_DIR}")


def load_stopwords(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
        return set()

STOPWORDS_FILE = os.path.join(PUBLIC_DIR, 'dictionary', 'stopwords_stemmed.txt')
stopwords = load_stopwords(STOPWORDS_FILE)

translator = str.maketrans(string.punctuation + '΄‘’“”«»…–', ' ' * (len(string.punctuation) + 9))
digit_punct_cleaner = re.compile(r'(?<=\d)[\.,](?=\d)')

# Apply to querry the same processing as in preprocess.py 
def preprocess_query(text):
    if not text: return ""

    text = digit_punct_cleaner.sub('', text.lower())
    text = text.translate(translator)
    words = text.split()
    
    cleaned_words = []
    
    for word in words:
        if word in stopwords or len(word) < 2:
            continue
            
        stemmed_upper = stemmer.stem_word(word.upper(), 'VBG')
        
        if stemmed_upper.islower():
            continue 
            
        stemmed_lower = stemmed_upper.lower()
        
        if stemmed_lower in stopwords:
            continue
            
        cleaned_words.append(stemmed_lower)

    return ' '.join(cleaned_words)

#Load tfidf models and datafile with unprocessed speeches
try:
    print("Loading models...")
    
    vec_path = os.path.join(PUBLIC_DIR, 'search_models', 'tfidf_vectorizer_speech.joblib')
    mat_path = os.path.join(PUBLIC_DIR, 'search_models', 'tfidf_matrix_speech.joblib')
    csv_path = os.path.join(PUBLIC_DIR, 'clean_full_speeches.csv')
    
    tfidf_vectorizer = joblib.load(vec_path) 
    tfidf_matrix = joblib.load(mat_path) 
    df = pd.read_csv(csv_path).fillna('')
    
    print("Processing dates...")
    df['date_obj'] = pd.to_datetime(df['sitting_date'], format='%d/%m/%Y', errors='coerce')
    df['year'] = df['date_obj'].dt.year.fillna(0).astype(int)
    
    print("Models and Data loaded successfully!")

except Exception as e:
    print(f"CRITICAL ERROR loading models: {e}")
    df = pd.DataFrame()
    tfidf_matrix = None
    tfidf_vectorizer = None


class SearchQuery(BaseModel):
    query: str
    top_k: int = 10

class TrendQuery(BaseModel):
    word: str


# Implements searching for speeches (1st tab of the website)
@app.post("/search")
def search_api(req: SearchQuery):
    if tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="Models not loaded properly.")

    processed_query = preprocess_query(req.query)
    
    if not processed_query:
        return {"results": [], "count": 0}

    query_vec = tfidf_vectorizer.transform([processed_query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[-req.top_k:][::-1]
    
    results = []
    for idx in top_indices:
        score = similarities[idx]
        if score > 0.05:
            row = df.iloc[idx]
            results.append({
                "member_name": row['member_name'],
                "sitting_date": row['sitting_date'],
                "political_party": row['political_party'],
                "speech_snippet": row['speech'][:300] + "...",
                "full_speech": row['speech'],
                "score": float(round(score, 4))
            })
    
    return {"results": results, "count": len(results)}

# Implements searching for usage of a specific word through the years
@app.post("/trend")
def get_word_trend(req: TrendQuery):
    if tfidf_matrix is None:
        raise HTTPException(status_code=500, detail="Models not loaded")
    
    processed_word = preprocess_query(req.word)
    
    if not processed_word:
        return {"data": []}

    target_token = processed_word.split()[0] if " " in processed_word else processed_word

    if target_token not in tfidf_vectorizer.vocabulary_:
        return {"data": [], "message": "Word not found in vocabulary", "token": target_token}
    
    word_index = tfidf_vectorizer.vocabulary_[target_token]
    word_scores = tfidf_matrix[:, word_index].toarray().flatten()

    temp_df = pd.DataFrame({
        'year': df['year'],
        'score': word_scores
    })

    trend_data = temp_df[temp_df['year'] > 0].groupby('year')['score'].sum().reset_index()
    trend_data = trend_data.sort_values('year')

    result = trend_data.to_dict(orient='records')
    
    return {"data": result, "token": target_token}