import csv
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
sample_data = "data/Greek_Parliament_Proceedings_1989_2020_DataSample.csv" 

def read_csv_as_list(file_path):
    with open(file_path, mode='r', newline='') as file:  #
        rows = []
        reader = csv.reader(file)
        header = next(reader)  # Retrieves and skips the header row
        print(header)
        for row in reader:
            rows.append(row)  # Each 'row' is a list: ['val1', 'val2', ...]
        return rows

simia_stixis = [',','.','!',';', '΄', '(', ')']

l_keywords = [
    "ο", "η", "το", "οι", "τα", "του", "της", "των", "τον", "τη", "την","τις",
    "ένας", "μια", "μία", "ένα", "ενός", "μιας", "μίας", 
    "στο", "στη", "στην", "στους", "στις", "στα", "στον",
    "εγώ", "εσύ", "αυτός", "αυτή", "αυτό","αυτόν", "αυτήν", "αυτό","αυτού","αυτής", "αυτών", "εμείς", "εσείς", "αυτοί", "αυτές", "αυτά",
    "μου", "σου", "του", "της", "μας", "σας", "τους", "δικός", "δική", "δικό", "εαυτού",
    "τούτος", "εκείνος", "τέτοιος", "τόσος", 
    "που", "ποιος", "ποια", "ποιο", "τι", "όποιος","όποια","όποιο","οποίος","οποία","οποίο", "οποιοσδήποτε", "πόσος",
    "κάποιος", "κάτι", "κανένας", "καμία", "κανένα", "καθένας", "καθεμία", "καθετί", "τίποτα",
    "από", "για", "με", "σε", "προς", "κατά", "παρά", "αντί", "δίχως", "χωρίς", "μέσω", "μετά", "πριν",
    "εν", "εκ", "επί", "περί", "υπό", "υπέρ", "ανά",
    "και", "κι", "αλλά", "ή", "είτε", "ούτε", "μήτε", "όμως", "ωστόσο", "επομένως",
    "ότι", "πως", "γιατί", "επειδή", "αφού", "ενώ", "καθώς", "αν", "εάν", "άμα", "ώστε", "μολονότι",
    "να", "θα", "ας", "μα", "δεν", "μη", "μην","ως",
    "έτσι", "πολύ", "λίγο", "τώρα", "τότε", "πια", "εκεί", "εδώ", "πάλι", "ακόμα", "ήδη","κ"]

def create_clean_csv(file_path, new_file_path="data/clean.csv"):
    with open(file_path, mode='r', newline='') as infile, \
        open(new_file_path, 'w', newline='', encoding='utf-8') as outfile:  #

        reader = csv.reader(infile) #
        writer = csv.writer(outfile) #

        header = next(reader)  # Retrieves and skips the header row
        writer.writerow(header)
        print(header)
        for row in reader:
            new_row = row.copy()
            new_row[-1] = ''
            speech = row[-1].lower()
            print(len(speech), end=' ')
            for simio_stixis in simia_stixis:
                speech = speech.replace(simio_stixis, '')
            for word in speech.split():
                if word not in l_keywords:
                    new_row[-1] += word + ' '
            #print(new_row)
            print(len(new_row[-1]))
            writer.writerow(new_row) #
        
def extract_top_keywords(texts, top_n=10):
    """
    Δέχεται μια λίστα κειμένων και επιστρέφει τις top_n λέξεις-κλειδιά 
    βάσει TF-IDF.
    """
    

    try:
        tfidf = TfidfVectorizer(stop_words=l_keywords, max_features=2000)
        tfidf_matrix = tfidf.fit_transform(texts)
        
        # Αθροίζουμε τα scores για κάθε λέξη σε όλα τα κείμενα της ομάδας
        sum_scores = tfidf_matrix.sum(axis=0)
        
        # Αντιστοίχιση λέξεων με scores
        words_freq = [(word, sum_scores[0, idx]) for word, idx in tfidf.vocabulary_.items()]
        words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
        
        return [word for word, score in words_freq[:top_n]]
    except ValueError:
        return [] # Επιστρέφει κενό αν δεν υπάρχουν αρκετά δεδομένα/λέξεις

# samples = read_csv_as_list(sample_data)
# print(len(samples))

create_clean_csv(sample_data)