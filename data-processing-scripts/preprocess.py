import re  
import csv
import string
import random
from greek_stemmer import stemmer


INPUT_FILE = "data/Greek_Parliament_Proceedings_1989_2020.csv" 
CLEAN_FILE = "parliament-search/public/clean.csv"
FULL_SPEECHES_FILE = "parliament-search/public/clean_full_speeches.csv"
SAMPLE_FILE = "data/random_sample.csv"
STOPWORDS_FILE = 'parliament-search/public/dictionary/stopwords_stemmed.txt'

CHARACTER_LIMIT = 50

translator = str.maketrans(string.punctuation + '΄‘’“”«»…–', ' ' * (len(string.punctuation) + 9))

digit_punct_cleaner = re.compile(r'(?<=\d)[\.,](?=\d)')

digit_punct_cleaner = re.compile(r'(?<=\d)[\.,](?=\d)')


def stemming(preprocessed_data):
    preprocessed_data1 = ''
    index = 0
    preprocessed_data = preprocessed_data.split(' ')
    for word in preprocessed_data:
        stemmed_word = stemmer.stem_word(word, 'VBG')
        if stemmed_word.islower():
            del preprocessed_data[index]
        else:
            preprocessed_data1 += stemmed_word.lower() + ' '
        index += 1
    return preprocessed_data1  

def create_random_sample(INPUT_FILE, output_file, sample_size):

    print("Counting total lines...")
    # PASS 1: Count total lines to determine the range
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        # Subtract 1 for the header
        total_lines = sum(1 for line in f) - 1
    
    print(f"Total data lines found: {total_lines}")

    if sample_size > total_lines:
        print("Sample size cannot be larger than the total number of lines.")
        return

    keep_indices = set(random.sample(range(1, total_lines + 1), sample_size))

    print(f"Extracting {sample_size} random lines...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8', newline='', errors='ignore') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        try:
            header = next(reader)
            writer.writerow(header)
        except StopIteration:
            print("File is empty.")
            return

        for index, row in enumerate(reader, start=1):
            if index in keep_indices:
                writer.writerow(row)

    print(f"Success! Sample saved to: {output_file}")

def load_stopwords(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
        return set()

def process_text_optimized(text, stopwords_list):
  
    # 1. Lowercase and Remove specific number formatting like 1.000
    text = digit_punct_cleaner.sub('', text.lower())
    
    # 2. Remove Punctuation (Fastest method in Python)
    text = text.translate(translator)
    
    # 3. Split into words
    words = text.split()
    
    cleaned_words = []
    
    for word in words:
        if word in stopwords_list or len(word) < 2:
            continue
            
        stemmed_upper = stemmer.stem_word(word.upper(), 'VBG')
        
        if stemmed_upper.islower():
            continue # Skip this word
            
        stemmed_lower = stemmed_upper.lower()
        
        if stemmed_lower in stopwords_list:
            continue
            
        cleaned_words.append(stemmed_lower)

    return ' '.join(cleaned_words)

def create_clean_csv(file_path, clean_file_path, clean_full_speeches_file_path, STOPWORDS_FILE):

    stopwords = load_stopwords(STOPWORDS_FILE)

    print(f"Ξεκινάει ο καθαρισμός του αρχείου {file_path}...")
    
    try:
        with open(file_path, mode='r', encoding='utf-8', errors='ignore') as infile, \
             open(clean_file_path, 'w', newline='', encoding='utf-8') as outfile_clean, \
            open(clean_full_speeches_file_path, 'w', newline='', encoding='utf-8') as outfile_full:

            reader = csv.reader(infile)
            writer_clean = csv.writer(outfile_clean)
            writer_clean_full_speeches = csv.writer(outfile_full)

            try:
                header = next(reader)
                writer_clean.writerow(header)
                writer_clean_full_speeches.writerow(header)
            except StopIteration:
                return

            count = 0
            
            for row in reader:
                if not row: continue
                
                original_speech = row[-1]
                
                if not original_speech:
                    row[-1] = ""
                    writer_clean.writerow(row)
                    continue
                        
                row[-1] = process_text_optimized(original_speech, stopwords)
                if len(row[-1]) >= CHARACTER_LIMIT:
                    writer_clean.writerow(row)
                    row[-1] = original_speech
                    writer_clean_full_speeches.writerow(row)
                
                count += 1
                if count % 1000 == 0:
                    print(f"Επεξεργάστηκαν {count} γραμμές...", end='\r')
        
        print(f"\nΟλοκληρώθηκε! Αποθηκεύτηκαν στο {clean_file_path} και στο {clean_full_speeches_file_path}")
                    
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {file_path} δεν βρέθηκε.")


create_clean_csv(SAMPLE_FILE, CLEAN_FILE, FULL_SPEECHES_FILE, STOPWORDS_FILE)

