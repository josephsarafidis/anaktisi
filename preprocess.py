import re  
import csv
import pandas as pd
import string
import matplotlib.pyplot as plt
import sys 
from sklearn.feature_extraction.text import TfidfVectorizer
import random
from greek_stemmer import stemmer



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

def create_random_sample(input_file, output_file, sample_size):

    print("Counting total lines...")
    # PASS 1: Count total lines to determine the range
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        # Subtract 1 for the header
        total_lines = sum(1 for line in f) - 1
    
    print(f"Total data lines found: {total_lines}")

    if sample_size > total_lines:
        print("Sample size cannot be larger than the total number of lines.")
        return

    keep_indices = set(random.sample(range(1, total_lines + 1), sample_size))

    print(f"Extracting {sample_size} random lines...")
    
    with open(input_file, 'r', encoding='utf-8', newline='', errors='ignore') as infile, \
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

def create_clean_csv(file_path, new_file_path, stopwords_file):

    stopwords = load_stopwords(stopwords_file)

    print(f"Ξεκινάει ο καθαρισμός του αρχείου {file_path}...")
    
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
                
                original_speech = row[-1]
                
                if not original_speech:
                    row[-1] = ""
                    writer.writerow(row)
                    continue

                row[-1] = process_text_optimized(original_speech, stopwords)
                
                writer.writerow(row)
                
                count += 1
                if count % 1000 == 0:
                    print(f"Επεξεργάστηκαν {count} γραμμές...", end='\r')
        
        print(f"\nΟλοκληρώθηκε! Αποθηκεύτηκε στο {new_file_path}")
                    
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {file_path} δεν βρέθηκε.")




