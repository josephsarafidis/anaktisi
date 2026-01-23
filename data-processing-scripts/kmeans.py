import pandas as pd
from sklearn.cluster import KMeans
import os

#STEP 6 of processing
#Perform clustering on speeches that have similar topics (according to LSI)

def perform_clustering_on_existing_topics(input_csv, n_clusters=5):
    print(f"\nΈναρξη Clustering (K-Means) με {n_clusters} ομάδες")
    
    try:
        df = pd.read_csv(input_csv)
        print("Το αρχείο φορτώθηκε επιτυχώς.")
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {input_csv} δεν βρέθηκε.")
        return

    topic_cols = [col for col in df.columns if col.startswith('Topic_')]
    
    if not topic_cols:
        print("Σφάλμα: Δεν βρέθηκαν στήλες Topic_X στο αρχείο.")
        return
        
    print(f"Θα χρησιμοποιηθούν {len(topic_cols)} στήλες για το clustering: {topic_cols}")
    
    X = df[topic_cols]

    # K-Means
    print(f"Ομαδοποίηση ομιλιών σε {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    
    df['Cluster_ID'] = kmeans.fit_predict(X)

    print("\nΚατανομή ομιλιών ανά ομάδα (Cluster ID):")
    distribution = df['Cluster_ID'].value_counts().sort_index()
    print(distribution)

    # Save file
    output_filename = 'parliament-search/public/clustering_results/speeches_with_clusters.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    
    print(f"\nΕπιτυχία! Το αρχείο με τις ομάδες αποθηκεύτηκε στο: {output_filename}")
    
   
    print("\nΥπολογισμός χαρακτηριστικών κάθε ομάδας...")
    cluster_means = df.groupby('Cluster_ID')[topic_cols].mean()
    cluster_means.to_csv('parliament-search/public/clustering_results/cluster_topic_analysis.csv', encoding='utf-8-sig')
    print("Αποθηκεύτηκε και η ανάλυση των ομάδων στο 'cluster_topic_analysis.csv'")


def print_speeches_by_cluster(csv_path, target_cluster_id, save_to_file=False):
    print(f"\n--- Αναζήτηση ομιλιών για το Cluster ID: {target_cluster_id} ---")
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Σφάλμα: Το αρχείο {csv_path} δεν βρέθηκε.")
        return

    if 'Cluster_ID' not in df.columns:
        print("Σφάλμα: Δεν βρέθηκε στήλη 'Cluster_ID'. Έχεις τρέξει το clustering;")
        return
    cluster_data = df[df['Cluster_ID'] == int(target_cluster_id)]
    
    count = len(cluster_data)
    print(f"Βρέθηκαν {count} ομιλίες στην ομάδα {target_cluster_id}.\n")
    
    if count == 0:
        return

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
        for i, (idx, row) in enumerate(cluster_data.iterrows()):
            print(f"--- Ομιλία {i+1}/{count} ---")
            print(f"Ομιλητής: {row.get('member_name', 'Άγνωστος')}") 
            print(f"Ημερομηνία: {row.get('sitting_date', '-')}")
            print(f"Κείμενο:")
            print(row['speech'])
            print("\n" + "="*50 + "\n")
    counts = df['Cluster_ID'].value_counts()

    print("Οι 5 μεγαλύτερες ομάδες:")
    print(counts.head(5))

    print("\nΟι 5 μικρότερες ομάδες:")
    print(counts.tail(5))

    print(f"\nΠόσες ομάδες έχουν κάτω από 5 ομιλίες; {(counts < 5).sum()}")


lsi_file = 'parliament-search/public/lsi_results/speech_vectors_lsi.csv' 

# Choose n_clusters
perform_clustering_on_existing_topics(lsi_file, n_clusters=100)

# The file we just created
speaches_with_clusters_file = "parliament-search/public/clustering_results/speeches_with_clusters.csv" 

#OPTIONAL - Print and save to file all speeches of a specified cluster
#print_speeches_by_cluster(speaches_with_clusters_file, target_cluster_id=27, save_to_file=True)    


