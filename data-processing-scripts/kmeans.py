import pandas as pd
from sklearn.cluster import KMeans
import os

def perform_clustering_on_existing_topics(input_csv, n_clusters=5):
    print(f"\nΈναρξη Clustering (K-Means) με {n_clusters} ομάδες")
    
    # 1. Φόρτωση του υπάρχοντος αρχείου (που έχει ήδη τα Topics)
    try:
        df = pd.read_csv(input_csv)
        print("Το αρχείο φορτώθηκε επιτυχώς.")
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {input_csv} δεν βρέθηκε.")
        return

    # 2. Επιλογή των στηλών που θα χρησιμοποιηθούν για την ομαδοποίηση
    # Ψάχνουμε αυτόματα τις στήλες που ξεκινάνε με 'Topic_'
    topic_cols = [col for col in df.columns if col.startswith('Topic_')]
    
    if not topic_cols:
        print("Σφάλμα: Δεν βρέθηκαν στήλες Topic_X στο αρχείο.")
        return
        
    print(f"Θα χρησιμοποιηθούν {len(topic_cols)} στήλες για το clustering: {topic_cols}")
    
    # Τα δεδομένα εκπαίδευσης είναι μόνο οι αριθμοί των Topics
    X = df[topic_cols]

    # 3. Εκτέλεση K-Means
    print(f"Ομαδοποίηση ομιλιών σε {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    
    # Fit & Predict: Βρίσκει τα κέντρα και δίνει ετικέτες
    df['Cluster_ID'] = kmeans.fit_predict(X)

    # 4. Στατιστικά: Πόσες ομιλίες πήγαν σε κάθε ομάδα;
    print("\nΚατανομή ομιλιών ανά ομάδα (Cluster ID):")
    distribution = df['Cluster_ID'].value_counts().sort_index()
    print(distribution)

    # 5. Αποθήκευση νέου αρχείου
    # Φτιάχνουμε φάκελο αν δεν υπάρχει
    os.makedirs('clustering_results', exist_ok=True)
    
    output_filename = 'parliament-search/public/clustering_results/speeches_with_clusters.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\nΕπιτυχία! Το αρχείο με τις ομάδες αποθηκεύτηκε στο: {output_filename}")
    
    # Προαιρετικό: Εξαγωγή μέσων τιμών των Topics ανά Cluster
    # Αυτό βοηθάει να καταλάβεις τι σημαίνει η κάθε ομάδα (π.χ. η ομάδα 0 έχει πολύ υψηλό Topic 4)
    print("\nΥπολογισμός χαρακτηριστικών κάθε ομάδας...")
    cluster_means = df.groupby('Cluster_ID')[topic_cols].mean()
    cluster_means.to_csv('parliament-search/public/clustering_results/cluster_topic_analysis.csv', encoding='utf-8-sig')
    print("Αποθηκεύτηκε και η ανάλυση των ομάδων στο 'cluster_topic_analysis.csv'")

import pandas as pd
import os

def print_speeches_by_cluster(csv_path, target_cluster_id, save_to_file=False):
    print(f"\n--- Αναζήτηση ομιλιών για το Cluster ID: {target_cluster_id} ---")
    
    # 1. Φόρτωση αρχείου
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {csv_path} δεν βρέθηκε.")
        return

    # 2. Έλεγχος αν υπάρχει η στήλη Cluster_ID
    if 'Cluster_ID' not in df.columns:
        print("Σφάλμα: Δεν βρέθηκε στήλη 'Cluster_ID'. Έχεις τρέξει το clustering;")
        return

    # 3. Φιλτράρισμα: Κρατάμε μόνο τις γραμμές της συγκεκριμένης ομάδας
    # Φροντίζουμε το target_cluster_id να είναι int, γιατί στο CSV είναι αριθμός
    cluster_data = df[df['Cluster_ID'] == int(target_cluster_id)]
    
    count = len(cluster_data)
    print(f"Βρέθηκαν {count} ομιλίες στην ομάδα {target_cluster_id}.\n")
    
    if count == 0:
        return

    # 4. Εκτύπωση (ή αποθήκευση)
    
    # Αν επιλέξεις save_to_file=True, τα γράφει σε αρχείο
    if save_to_file:
        filename = f"cluster_{target_cluster_id}_speeches.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for i, (idx, row) in enumerate(cluster_data.iterrows()):
                f.write(f"--- Ομιλία {i+1}/{count} ---\n")
                f.write(f"Ομιλητής: {row['member_name']}\n")
                f.write(f"Ημερομηνία: {row['sitting_date']}\n")
                f.write(f"Κείμενο:\n{row['speech']}\n")
                f.write("\n" + "="*50 + "\n\n")
        print(f"Οι ομιλίες αποθηκεύτηκαν στο αρχείο: {filename}")
        
    else:
        # Αλλιώς τα τυπώνει στην οθόνη
        for i, (idx, row) in enumerate(cluster_data.iterrows()):
            print(f"--- Ομιλία {i+1}/{count} ---")
            print(f"Ομιλητής: {row.get('member_name', 'Άγνωστος')}") # .get για ασφάλεια
            print(f"Ημερομηνία: {row.get('sitting_date', '-')}")
            print(f"Κείμενο:")
            print(row['speech'])
            print("\n" + "="*50 + "\n")
    # Υποθέτω ότι το df είναι το DataFrame σου με το Cluster_ID
    counts = df['Cluster_ID'].value_counts()

    print("Οι 5 μεγαλύτερες ομάδες:")
    print(counts.head(5))

    print("\nΟι 5 μικρότερες ομάδες:")
    print(counts.tail(5))

    print(f"\nΠόσες ομάδες έχουν κάτω από 5 ομιλίες; {(counts < 5).sum()}")


# Βάλε εδώ το όνομα του αρχείου που ΕΧΕΙΣ ΗΔΗ (με τα Topics)
# Π.χ. 'lsi_results/speech_vectors_lsi.csv' ή όπως αλλιώς το λένε
lsi_file = 'parliament-search/public/lsi_results/speech_vectors_lsi.csv' 

# Επιλέγεις πόσες ομάδες θες (π.χ. 5)
perform_clustering_on_existing_topics(lsi_file, n_clusters=100)


# Το αρχείο που έφτιαξες στο προηγούμενο βήμα
speaches_with_clusters_file = "parliament-search/public/clustering_results/speeches_with_clusters.csv" 

print_speeches_by_cluster(speaches_with_clusters_file, target_cluster_id=27)    


