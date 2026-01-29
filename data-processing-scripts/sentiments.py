import pandas as pd
import re
from datetime import datetime

# --- 1. ΛΕΞΙΚΟ ΣΥΝΑΙΣΘΗΜΑΤΟΣ ---
POSITIVE_WORDS = {
    'καλό', 'καλή', 'επιτυχία', 'ανάπτυξη', 'πρόοδος', 'θετικό', 'ελπίδα', 'λύση', 
    'εξαιρετική', 'δίκαιο', 'σωστό', 'συμφωνώ', 'στήριξη', 'δημοκρατία', 'ελευθερία',
    'ασφάλεια', 'σταθερότητα', 'ευημερία', 'κέρδος', 'άριστα', 'μπράβο', 'συγχαρητήρια',
    'δικαιοσύνη', 'όραμα', 'εμπιστοσύνη', 'αξιοπρέπεια', 'αλληλεγγύη'
}

NEGATIVE_WORDS = {
    'κακό', 'λάθος', 'αποτυχία', 'κρίση', 'ύφεση', 'καταστροφή', 'ντροπή', 'αίσχος',
    'πρόβλημα', 'ανεργία', 'φτώχεια', 'σκάνδαλο', 'έγκλημα', 'κίνδυνος', 'απειλή',
    'ανικανότητα', 'ψέμα', 'απάτη', 'βία', 'χρέος', 'μνημόνιο', 'δυστυχία', 'αντίθετος',
    'διαφθορά', 'υποκρισία', 'κατάρρευση', 'εξαθλίωση', 'πανικός'
}

NEGATIONS = {'δεν', 'μη', 'μην', 'όχι', 'κανείς', 'ποτέ', 'ουδέποτε', 'ούτε'}

def calculate_sentiment(text):
    if not isinstance(text, str):
        return 0.0
    
    words = re.findall(r'\w+', text.lower())
    score = 0
    total_significant_words = 0
    
    for i, word in enumerate(words):
        val = 0
        if word in POSITIVE_WORDS:
            val = 1
        elif word in NEGATIVE_WORDS:
            val = -1
            
        if val != 0:
            # Έλεγχος άρνησης (π.χ. "δεν υπάρχει ελπίδα" -> αρνητικό γίνεται θετικό;)
            # Προσοχή: "δεν υπάρχει ελπίδα" = NEGATION + POSITIVE = -1 (κακό)
            # Η λογική εδώ: val * -1. Αν val=1 (ελπίδα), γίνεται -1. Σωστό.
            if i > 0 and words[i-1] in NEGATIONS:
                val *= -1
            elif i > 1 and words[i-2] in NEGATIONS:
                val *= -1
            
            score += val
            total_significant_words += 1
            
    if total_significant_words == 0:
        return 0.0
    
    return score / total_significant_words

# --- 2. ΦΟΡΤΩΣΗ ---
print("Φόρτωση δεδομένων...")
# Προσοχή στο path του αρχείου σου
df = pd.read_csv('parliament-search/public/clean_full_speeches.csv', 
                 usecols=['sitting_date', 'speech']) 

df['sitting_date'] = pd.to_datetime(df['sitting_date'], format='%d/%m/%Y', errors='coerce')
df = df.dropna(subset=['sitting_date', 'speech'])

# --- 3. ΥΠΟΛΟΓΙΣΜΟΣ ---
print("Υπολογισμός συναισθήματος ανά ομιλία...")
df['sentiment'] = df['speech'].apply(calculate_sentiment)

# --- 4. ΟΜΑΔΟΠΟΙΗΣΗ (ΜΟΝΟ ΣΥΝΟΛΙΚΑ) ---
print("Ομαδοποίηση ανά έτος...")
df['year'] = df['sitting_date'].dt.year

# Υπολογίζουμε τον μέσο όρο του 'sentiment' για κάθε έτος
final_result = df.groupby('year')['sentiment'].mean().reset_index()

# Προαιρετικό: Στρογγυλοποίηση για μικρότερο αρχείο
final_result['sentiment'] = final_result['sentiment'].round(4)

# --- 5. EXPORT ---
output_file = 'parliament-search/public/sentiment_results.json'
final_result.to_json(output_file, orient='records')
print(f"Έτοιμο! Αποθηκεύτηκε στο {output_file}")
# Θα παράγει κάτι σαν: [{"year":1989, "sentiment":0.05}, {"year":1990, "sentiment":-0.02}, ...]