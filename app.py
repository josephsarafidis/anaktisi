
import re  
import csv
import pandas as pd
import string
import matplotlib.pyplot as plt
import sys 
from sklearn.feature_extraction.text import TfidfVectorizer
import random

# Αρχεία εισόδου/εξόδου
input_file = "data/Greek_Parliament_Proceedings_1989_2020.csv"  # Άλλαξε το αν χρειάζεται
clean_file = "data/clean.csv"
sample_file = "data/random_sample.csv"
csv.field_size_limit(sys.maxsize)




l_keywords = set([
    # --- Βασικά (Άρθρα, Αντωνυμίες, Προθέσεις, Σύνδεσμοι) ---
    "ο", "γι", "η", "το", "οι", "τα", "του", "της", "των", "τον", "τη", "την", "τις",
    "ένας", "μια", "μία", "ένα", "ενός", "μιας", "μίας", "δε", "ακριβώς", "εξής", "βέβαια",
    "στο", "στη", "στην", "στους", "στις", "στα", "στον", "είμαστε", "είμαι", "είστε","όλους","κανείς",
    "εγώ", "εσύ", "αυτός", "αυτή", "αυτό", "αυτόν", "αυτήν", "αυτού", "αυτής", "αυτών", "καλά",
    "εμείς", "εσείς", "αυτοί", "αυτές", "αυτά", "κατ", "απ", "πει", "ξέρω", 
    "μου", "σου", "του", "της", "μας", "σας", "τους", "δικός", "δική", "δικό", "εαυτού",
    "τούτος", "εκείνος", "τέτοιος", "τόσος",
    "που", "ποιος", "ποια", "ποιο", "τι", "όποιος", "όποια", "όποιο", "οποίος", "οποία", 
    "οποίο", "οποιοσδήποτε", "πόσος",
    "κάποιος", "κάτι", "κανένας", "καμία", "κανένα", "καθένας", "καθεμία", "καθετί", "τίποτα",
    "από", "για", "με", "σε", "προς", "κατά", "παρά", "αντί", "δίχως", "χωρίς", "μέσω", "μετά", "πριν",
    "εν", "εκ", "επί", "περί", "υπό", "υπέρ", "ανά",
    "και", "κι", "αλλά", "ή", "είτε", "ούτε", "μήτε", "όμως", "ωστόσο", "επομένως",
    "ότι", "πως", "γιατί", "επειδή", "αφού", "ενώ", "καθώς", "αν", "εάν", "άμα", "ώστε", "μολονότι",
    "να", "θα", "ας", "μα", "δεν", "μη", "μην", "ως","ευχαριστούμε","όπως","ορίστε","όχι","ναι",
    "άλλο","μάλιστα","λοιπόν", "διότι", "βεβαίως", "κάθε", "μέσα", "επίσης", "άλλη",
    # --- Ρήματα Ρουτίνας & Γενικά ---
    "είναι", "ήταν", "έχω", "είχε", "έχεις", "έχει", "έχετε", "έχουμε", "έχουν","είχατε",
    "κάνει", "κάνουμε", "κάνετε", "λέω", "λες", "λέτε", "λέμε", "νομίζω", "πιστεύω",
    "θέλω", "θέλουμε", "θέλετε", "πρέπει", "γίνεται", "φορά", "πράγμα", "πράγματα",
    "εδώ", "εκεί", "πού", "πώς", "πότε", "όλα", "όλοι", "όλες", "όλο", "κάνω", "μπορώ",
    "έτσι", "πολύ", "λίγο", "τώρα", "τότε", "πια", "πάλι", "ακόμα", "ήδη", "μόνο", "κ", "κο", "ξέρετε",    "ευχαριστούμε","μάλιστα","είπε", "αφορά", "λέει", "πάρα","κλείσει","πω","μπορεί","γίνει",
    "συνεπώς","δηλαδή","έγινε","ήθελα", "πείτε", "είπα", "ερωτάται", "υπάρχει", "υπάρχουν", "είπατε",

    # --- Προσφωνήσεις & Ευγένειες Βουλής ---
    "κύριος","κύριε", "κυρία", "κύριοι", "κύριο", "κυρίες", "συνάδελφε", "συνάδελφος", "συνάδελφοι", "αγαπητέ", "αγαπητοί",
    "πρόεδρε", "υπουργέ","υπουργός","υπουργό", "υπουργείου", "υφυπουργέ", "βουλευτή","βουλευτής", "βουλευτές", 
    "παρακαλώ", "ευχαριστώ", "λόγο", "ομιλία", "τοποθέτηση",
    
    # --- Ορολογία Βουλής & Διαδικαστικά (Noise words για την ανάλυση) ---
    "νομοσχέδιο", "σχέδιο", "νόμου", "νόμος", "νόμοι", 
    "άρθρο","άρθρου", "άρθρα", "διάταξη", "διατάξεις", "παράγραφος",
    "τροπολογία", "τροπολογίες", "επιτροπή", "επιτροπές", "τροποποιήθηκε",
    "ολομέλεια", "βουλή", "βουλής", "αίθουσα", "εδρανα",
    "πρακτικά", "συνεδρίαση", "ημερήσια", "διάταξη",
    "ψηφοφορία", "ψήφιση", "ψήφο", "συζήτηση", "ερώτηση", "επίκαιρη", "σώμα",
    "εισηγητής", "εισηγήτρια", "κοινοβουλευτικός", "εκπρόσωπος", 
    "κυβέρνηση", "κυβέρνησης", "αντιπολίτευση", "αξιωματική",
    "υπουργείο", "υπουργεία", "κόμμα", "κόμματα","υφυπουργός", "πλειοψηφία", "δεκτό", "θέμα",
    
    # --- Χρονικά & Ποσοτικά ---
    "σήμερα", "χθες", "αύριο", "φέτος", "πέρυσι","σύντομα","παρών","όταν", "αριθμό",
    "έτος", "έτη", "χρόνια", "ημέρα", "μέρες", "χρόνο", "λεπτά", "ώρα","λεπτό", "στιγμή",
    "ευρώ", "εκατομμύρια", "δισεκατομμύρια", "χιλιάδες", "ποσό", "ποσά", "νούμερα",
    "ένα","ένας", "έναν", "δύο", "τρεις", "τρία", "τέσσερις", "πέντε","έξι","επτά", "δέκα", "μέχρι"
])

#simia_stixis = [',','.','!',';', '΄', '(', ')', '«', '»']


# Πίνακας για γρήγορη αφαίρεση στίξης (περιλαμβάνει και ελληνικά σημεία)
punctuation_map = str.maketrans('', '', string.punctuation + '΄‘’“”«»…')


def create_random_sample(input_file, output_file, sample_size):
    """
    Creates a random sample of n lines from a large CSV file.
    """
    print("Counting total lines...")
    # PASS 1: Count total lines to determine the range
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        # Subtract 1 for the header
        total_lines = sum(1 for line in f) - 1
    
    print(f"Total data lines found: {total_lines}")

    if sample_size > total_lines:
        print("Sample size cannot be larger than the total number of lines.")
        return

    # Generate a set of random indices to keep (range starts at 1 to skip header)
    # random.sample is efficient and ensures unique indices
    keep_indices = set(random.sample(range(1, total_lines + 1), sample_size))

    print(f"Extracting {sample_size} random lines...")
    
    # PASS 2: Read and Write specific lines
    with open(input_file, 'r', encoding='utf-8', newline='', errors='ignore') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # 1. Always write the header
        try:
            header = next(reader)
            writer.writerow(header)
        except StopIteration:
            print("File is empty.")
            return

        # 2. Iterate through rows and write only if index is in our random set
        for index, row in enumerate(reader, start=1):
            if index in keep_indices:
                writer.writerow(row)

    print(f"Success! Sample saved to: {output_file}")


# 2. Συνάρτηση Καθαρισμού CSV

# Φτιάχνουμε έναν πίνακα που μετατρέπει ΟΛΑ τα σημεία στίξης σε ΚΕΝΑ
# Έτσι το "όχι,ναι" γίνεται "όχι ναι" και δεν κολλάνε οι λέξεις.
translator = str.maketrans(string.punctuation + '΄‘’“”«»…–', ' ' * (len(string.punctuation) + 9))

def create_clean_csv(file_path, new_file_path):
    print("Ξεκινάει ο καθαρισμός του αρχείου...")
    
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as infile, \
             open(new_file_path, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            try:
                header = next(reader)
                writer.writerow(header)
            except StopIteration:
                return

            count = 0
            for row in reader:
                if not row: continue
                
                # 1. Lowercase
                original_speech = row[-1].lower()
                
                # 2. Αφαίρεση ΟΛΩΝ των σημείων στίξης με τη μία (αντικατάσταση με κενό)
                original_speech = re.sub(r'(?<=\d)[\.,](?=\d)', '', original_speech)                         
                # Χρησιμοποιούμε το translator που φτιάξαμε πιο πάνω
                no_punct = original_speech.translate(translator)
                
                # 3. Split και φιλτράρισμα
                # Το split() χωρίς ορίσματα καθαρίζει αυτόματα τα πολλαπλά κενά
                cleaned_words = [word for word in no_punct.split() if word not in l_keywords and len(word) > 1]
                
                row[-1] = ' '.join(cleaned_words)
                
                writer.writerow(row)
                count += 1
                if count % 1000 == 0:
                    print(f"Επεξεργάστηκαν {count} γραμμές...", end='\r')
                    
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {file_path} δεν βρέθηκε.")

def extract_and_plot_keywords(csv_path, top_n=50):
    print("Φόρτωση δεδομένων στο Pandas...")
    try:
        df = pd.read_csv(csv_path)
        
        # Έλεγχος αν υπάρχει στήλη speech
        col_name = 'speech' if 'speech' in df.columns else df.columns[-1]
        
        # --- ΔΙΟΡΘΩΣΗ ΓΙΑ NAN ---
        # 1. Αφαίρεση γραμμών που είναι πραγματικά κενές (NaN)
        df = df.dropna(subset=[col_name])
        
        # 2. Μετατροπή σε string για ασφάλεια
        df[col_name] = df[col_name].astype(str)
        
        # 3. Αφαίρεση γραμμών που έχουν τη λέξη "nan" (αν δημιουργήθηκε από μετατροπή)
        df = df[df[col_name].str.lower() != 'nan']
        
        # 4. Αφαίρεση πολύ μικρών κειμένων (π.χ. σκουπίδια κάτω από 3 χαρακτήρες)
        df = df[df[col_name].str.len() > 3]
        # ------------------------

        text_data = df[col_name].tolist()

        if not text_data:
            print("Δεν βρέθηκαν δεδομένα κειμένου.")
            return

        print(f"Ανάλυση σε {len(text_data)} ομιλίες...")
        print("Υπολογισμός TF-IDF...")
        
        # max_df=0.67: Αγνοεί λέξεις που εμφανίζονται στο 67% των εγγράφων
        tfidf = TfidfVectorizer(max_features=1000, max_df=0.67)
        tfidf_matrix = tfidf.fit_transform(text_data)

        # Άθροισμα σκορ για κάθε λέξη
        sum_scores = tfidf_matrix.sum(axis=0)
        
        # Δημιουργία λίστας (λέξη, σκορ)
        words_freq = [(word, sum_scores[0, idx]) for word, idx in tfidf.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        
        # Επιλογή των top_n
        top_words = words_freq[:top_n]
        labels = [w[0] for w in top_words]
        scores = [w[1] for w in top_words]

        # 4. Οπτικοποίηση
        plt.figure(figsize=(10, 6))
        plt.barh(labels, scores, color='skyblue')
        plt.gca().invert_yaxis() # Οι σημαντικότερες λέξεις πάνω
        plt.title(f'Top {top_n} Λέξεις-Κλειδιά (TF-IDF)')
        plt.xlabel('TF-IDF Score')
        plt.tight_layout() # Για να μην κόβονται τα γράμματα
        plt.show()
        
        print("\nTop Keywords:", labels)

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
    """
    Δείχνει πώς αλλάζουν οι λέξεις-κλειδιά για ένα συγκεκριμένο κόμμα/βουλευτή ανά έτος.
    target_entity: π.χ. 'νέα δημοκρατία'
    entity_type: 'political_party' ή 'member_name'
    """
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

#create_clean_csv(input_file, clean_file)

# Βήμα 2: Ανάλυση & Γράφημα
#extract_and_plot_keywords(clean_file)

# --- MAIN EXECUTION ---

# 1. Καθαρισμός (αν δεν έχει γίνει ήδη)
# create_clean_csv(input_file, clean_file)

# 2. Keywords ανά Κόμμα (Σύγκριση κομμάτων μεταξύ τους)
# Προσοχή: Βεβαιώσου ότι το CSV έχει στήλη 'political_party'
analyze_group_keywords(clean_file, group_col='political_party', top_n=7)

# 3. Keywords ανά Βουλευτή (Μπορεί να αργήσει λίγο αν είναι πολλοί)
analyze_group_keywords(clean_file, group_col='member_name', top_n=5)

# 4. Χρονική εξέλιξη για ένα συγκεκριμένο κόμμα
# Δοκίμασε με 'πασοκ', 'νέα δημοκρατία', 'συνασπισμός ριζοσπαστικής αριστεράς' κλπ.
analyze_keywords_over_time(clean_file, target_entity='νέα δημοκρατία', entity_type='political_party')