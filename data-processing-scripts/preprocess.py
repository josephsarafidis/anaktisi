import re  
import csv
import sys
import string
import random
from greek_stemmer import stemmer
from functools import lru_cache
from multiprocessing import Pool, cpu_count

#STEP 2 of processing
#Process the speeches while removing the ones that are too short and create a csv file of processed version
#and a csv file of unprocessed version

INPUT_FILE = "data/Greek_Parliament_Proceedings_1989_2020.csv" 
CLEAN_FILE = "parliament-search/public/clean.csv"
FULL_SPEECHES_FILE = "parliament-search/public/clean_full_speeches.csv"
SAMPLE_FILE = "data/random_sample.csv"
STOPWORDS_FILE = 'parliament-search/public/dictionary/stopwords_stemmed.txt'

CHARACTER_LIMIT = 50

translator = str.maketrans(string.punctuation + '΄‘’“”«»…–', ' ' * (len(string.punctuation) + 9))

digit_punct_cleaner = re.compile(r'(?<=\d)[\.,](?=\d)')

csv.field_size_limit(sys.maxsize)

# Global variable for the worker processes
worker_stopwords = None

@lru_cache(maxsize=100000)
def cached_stem(word):
    # No .upper() needed here anymore, input is already Upper
    return stemmer.stem_word(word, 'VBG')

def init_worker(stopwords_list):
    """Initialize worker with stopwords to avoid pickling overhead."""
    global worker_stopwords
    worker_stopwords = stopwords_list

def create_random_sample(INPUT_FILE, output_file, sample_size):

    print("Counting total lines...")
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
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
            # OPTIMIZATION: Load stopwords as UPPERCASE directly
            return set(line.strip().upper() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")
        return set()

def process_text_optimized(text, stopwords_list):
  
    # 1. Uppercase entire text ONCE (matches Stemmer requirement)
    # Remove number formatting 
    text = digit_punct_cleaner.sub('', text.upper())
    
    # 2. Remove Punctuation 
    text = text.translate(translator)
    
    words = text.split()
    
    cleaned_words = []
    
    # Optimization: Bind methods to local variables for faster lookup inside loop
    append_word = cleaned_words.append
    
    for word in words:
    # 4. Skip stopwords (checking against UPPERCASE set)
        if word in stopwords_list:
            continue
            
    # 5. Stem (word is already UPPER, no conversion needed)
        stemmed_upper = cached_stem(word)
        
        # 6. Post-stemming checks
        # Logic check: If stem became lower, stemmer rejected it or it's invalid
        if stemmed_upper.islower():
            continue 
            
        if stemmed_upper in stopwords_list:
            continue
            
        # Only convert to lower at the very end for output
        append_word(stemmed_upper.lower())

    return ' '.join(cleaned_words)

def process_row_wrapper(row):
    if not row: return None
    
    original_speech = row[-1]
    
    if not original_speech:
        row[-1] = ""
        # Return tuple: (type, data)
        return ('empty', row)
            
    processed_text = process_text_optimized(original_speech, worker_stopwords)
    
    #Skip speech if it is too short
    if len(processed_text) >= CHARACTER_LIMIT:
        clean_row = list(row)
        clean_row[-1] = processed_text
        
        full_row = list(row)
        full_row[-1] = original_speech
        
        return ('valid', (clean_row, full_row))
    
    return None

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
            
            # Create a pool of workers to process rows in parallel
            with Pool(processes=cpu_count(), initializer=init_worker, initargs=(stopwords,)) as pool:
                
                # imap allows processing the file as a stream without loading everything into RAM
                for result in pool.imap(process_row_wrapper, reader, chunksize=100):
                    if result is None:
                        continue
                        
                    result_type, data = result
                    
                    if result_type == 'empty':
                        writer_clean.writerow(data)
                    elif result_type == 'valid':
                        clean_row, full_row = data
                        writer_clean.writerow(clean_row)
                        writer_clean_full_speeches.writerow(full_row)
                    
                    count += 1
                    if count % 1000 == 0:
                        print(f"Επεξεργάστηκαν {count} γραμμές...", end='\r')
        
        print(f"\nΟλοκληρώθηκε! Αποθηκεύτηκαν στο {clean_file_path} και στο {clean_full_speeches_file_path}")
                    
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {file_path} δεν βρέθηκε.")

#OPTIONAL: Create another random sample of the original file
#create_random_sample(INPUT_FILE, SAMPLE_FILE, 10000)
create_clean_csv(INPUT_FILE, CLEAN_FILE, FULL_SPEECHES_FILE, STOPWORDS_FILE)