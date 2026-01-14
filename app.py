
import re  
import csv
import pandas as pd
import string
import matplotlib.pyplot as plt
import sys 
from sklearn.feature_extraction.text import TfidfVectorizer
import random
from greek_stemmer import stemmer
from preprocess import create_clean_csv

# Αρχεία εισόδου/εξόδου
input_file = "data/Greek_Parliament_Proceedings_1989_2020.csv"  # Άλλαξε το αν χρειάζεται
clean_file = "data/clean.csv"
sample_file = "data/random_sample.csv"
sample_small_file = "data/Greek_Parliament_Proceedings_1989_2020_DataSample.csv"
stopwords_file = 'dictionary/stopwords_stemmed.txt'
csv.field_size_limit(sys.maxsize)

def extract_talk_keywords(csv_path, talk_index, top_n=50):
    print("Φόρτωση δεδομένων στο Pandas...")
    try:
        df = pd.read_csv(csv_path)
        col_name = 'speech' if 'speech' in df.columns else df.columns[-1]
        
        # Καθαρισμός δεδομένων (όπως πριν)
        df = df.dropna(subset=[col_name])
        df[col_name] = df[col_name].astype(str)
        df = df[df[col_name].str.lower() != 'nan']
        df = df[df[col_name].str.len() > 3]

        text_data = df[col_name].tolist()
        if not text_data:
            print("Δεν βρέθηκαν δεδομένα κειμένου.")
            return

        print(f"Ανάλυση σε {len(text_data)} ομιλίες...")
        
        # Υπολογισμός TF-IDF
        tfidf = TfidfVectorizer(max_df=0.85) # max_df για να φιλτράρουμε πολύ κοινές λέξεις
        tfidf_matrix = tfidf.fit_transform(text_data)
        
        # 1. Παίρνουμε όλα τα ονόματα των λέξεων (features)
        feature_names = tfidf.get_feature_names_out()

        # 2. Απομονώνουμε τη συγκεκριμένη ομιλία (γραμμή)
        # Μετατρέπουμε τη sparse γραμμή σε array και μετά σε λίστα
        row_data = tfidf_matrix[talk_index].toarray().flatten()

        # 3. Συσχετίζουμε κάθε λέξη με το score της
        # Δημιουργούμε μια λίστα από tuples: (λέξη, score)
        word_score_list = []
        for i in range(len(row_data)):
            if row_data[i] > 0: # Κρατάμε μόνο λέξεις που υπάρχουν στην ομιλία
                word_score_list.append((feature_names[i], row_data[i]))

        # 4. Ταξινόμηση (Sorting) με βάση το score (το 2ο στοιχείο του tuple)
        # reverse=True για να έχουμε τα μεγαλύτερα scores πάνω
        word_score_list.sort(key=lambda x: x[1], reverse=True)

        # 5. Εκτύπωση αποτελεσμάτων
        print(f"\n--- Top {top_n} Keywords για την ομιλία #{talk_index} ---")
        for word, score in word_score_list[:top_n]:
            print(f"{word:20} : {score:.4f}")

    except Exception as e:
        print(f"Προέκυψε σφάλμα κατά την ανάλυση: {e}")

def analyze_group_keywords(csv_path, group_col, top_n=10):
    """
    Βρίσκει τα keywords ανά ομάδα (π.χ. ανά Κόμμα ή ανά Βουλευτή).
    group_col: 'political_party' ή 'member_name'
    """
    print(f"\n--- Ανάλυση Keywords ανά {group_col} ---")
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['speech'])
    df['speech'] = df['speech'].astype(str)

    # 1. Ομαδοποίηση: Ενώνουμε όλες τις ομιλίες κάθε ομάδας σε μία μεγάλη συμβολοσειρά
    # Αυτό βοηθάει το TF-IDF να βρει τι είναι ΜΟΝΑΔΙΚΟ για κάθε κόμμα
    grouped_df = df.groupby(group_col)['speech'].apply(lambda x: ' '.join(x)).reset_index()
    
    # Φίλτρο: Κρατάμε μόνο κόμματα/βουλευτές με αρκετό κείμενο (π.χ. > 5000 χαρακτήρες)
    grouped_df = grouped_df[grouped_df['speech'].str.len() > 5000]

    print(f"Δημιουργήθηκαν {len(grouped_df)} ομαδοποιημένα έγγραφα.")

    # 2. TF-IDF
    tfidf = TfidfVectorizer(max_features=2000, max_df=0.8) # max_df=0.8: αγνοούμε λέξεις που λένε ΟΛΑ τα κόμματα
    tfidf_matrix = tfidf.fit_transform(grouped_df['speech'])
    feature_names = tfidf.get_feature_names_out()

    # 3. Εξαγωγή αποτελεσμάτων για κάθε ομάδα
    results = {}
    dense = tfidf_matrix.todense()
    
    for i, row in grouped_df.iterrows():
        entity = row[group_col]
        # Παίρνουμε τη γραμμή του πίνακα για το συγκεκριμένο κόμμα
        episode_vector = dense[i].tolist()[0]
        # Ζευγαρώνουμε (λέξη, σκορ) και ταξινομούμε
        phrase_scores = [pair for pair in zip(feature_names, episode_vector) if pair[1] > 0]
        sorted_phrases = sorted(phrase_scores, key=lambda t: t[1] * -1)
        
        # Κρατάμε τις top_n λέξεις
        top_words = [word for word, score in sorted_phrases[:top_n]]
        results[entity] = top_words
        
        print(f"{entity}: {', '.join(top_words)}")
        
    return results

def analyze_keywords_over_time(csv_path, target_entity, entity_type='political_party'):

    print(f"\n--- Χρονική Ανάλυση για: {target_entity} ---")
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['speech', 'sitting_date'])
    
    # Μετατροπή ημερομηνίας και εξαγωγή έτους
    df['year'] = pd.to_datetime(df['sitting_date'], errors='coerce').dt.year
    df = df.dropna(subset=['year']) # Αφαιρούμε άκυρες ημερομηνίες
    df['year'] = df['year'].astype(int)

    # Φιλτράρουμε μόνο το κόμμα/βουλευτή που μας ενδιαφέρει
    # (Χρησιμοποιούμε lower() για σιγουριά)
    subset = df[df[entity_type].str.lower() == target_entity.lower()]
    
    if subset.empty:
        print(f"Δεν βρέθηκαν δεδομένα για {target_entity}")
        return

    # Ομαδοποίηση ανά Έτος
    grouped_by_year = subset.groupby('year')['speech'].apply(lambda x: ' '.join(x)).reset_index()
    
    # TF-IDF ανά έτος (treat each year as a document)
    tfidf = TfidfVectorizer(max_features=100, max_df=0.9)
    try:
        tfidf_matrix = tfidf.fit_transform(grouped_by_year['speech'])
    except ValueError:
        print("Δεν υπάρχουν αρκετά δεδομένα για TF-IDF.")
        return

    feature_names = tfidf.get_feature_names_out()
    dense = tfidf_matrix.todense()

    # Plotting Setup
    years = grouped_by_year['year'].tolist()
    top_keywords_per_year = []

    print("\nTop words ανά έτος:")
    for i, year in enumerate(years):
        vector = dense[i].tolist()[0]
        phrase_scores = zip(feature_names, vector)
        sorted_phrases = sorted(phrase_scores, key=lambda t: t[1] * -1)
        
        # Παίρνουμε τις 3 πιο σημαντικές λέξεις για το plot
        top_3 = [w[0] for w, s in sorted_phrases[:3]]
        top_keywords_per_year.append(", ".join(top_3))
        print(f"{year}: {', '.join(top_3)}")

    # Visualization: Απλό timeline με τις λέξεις
    plt.figure(figsize=(12, 8))
    plt.plot(years, [1]*len(years), 'bo-') # Dummy line
    
    # Προσθήκη κειμένου στο γράφημα
    for i, txt in enumerate(top_keywords_per_year):
        plt.annotate(txt, (years[i], 1), textcoords="offset points", xytext=(0, 10 if i%2==0 else -20), ha='center', rotation=45)
    
    plt.title(f"Εξέλιξη θεματολογίας: {target_entity}")
    plt.xlabel("Έτος")
    plt.yticks([]) # Κρύβουμε τον άξονα Υ
    plt.tight_layout()
    plt.show()

#create_random_sample(input_file, sample_file, 100000)




create_clean_csv(sample_small_file, clean_file, stopwords_file)

extract_talk_keywords(clean_file, 50)

analyze_group_keywords(clean_file, 'political_party')
