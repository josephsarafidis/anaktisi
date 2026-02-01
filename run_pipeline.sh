#!/bin/bash
set -e

if [ ! -f "data/random_sample.csv" ]; then
    echo "ΣΦΑΛΜΑ: Το αρχείο data/random_sample.csv δεν βρέθηκε!"
    exit 1
fi

python data-processing-scripts/stem.py

python data-processing-scripts/preprocess.py

python data-processing-scripts/tfidf.py

python data-processing-scripts/similarities.py

python data-processing-scripts/lsi.py

python data-processing-scripts/kmeans.py

python data-processing-scripts/sentiments.py

echo "--- Η ΕΠΕΞΕΡΓΑΣΙΑ ΟΛΟΚΛΗΡΩΘΗΚΕ ΕΠΙΤΥΧΩΣ ---"