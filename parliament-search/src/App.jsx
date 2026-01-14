import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import './App.css';

// --- COMPONENTS ΓΙΑ ΚΑΘΕ TAB ---

// 1. Component Αναζήτησης (Ο κώδικας που ήδη είχαμε, βελτιωμένος)
const SearchTab = () => {
  const [data, setData] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Φόρτωσε το αρχείο με τις ομιλίες (ή το δείγμα)
    Papa.parse('public/clean.csv', { // ΑΛΛΑΞΕ ΤΟ ΟΝΟΜΑ ΑΝ ΧΡΕΙΑΖΕΤΑΙ
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        setData(result.data);
        setLoading(false);
      }
    });
  }, []);

  const filteredSpeeches = data.filter(s => {
    if (!searchTerm) return true;
    if (!s.member_name || !s.speech) return false;
    const term = searchTerm.toLowerCase();
    return (
      s.member_name.toLowerCase().includes(term) ||
      s.speech.toLowerCase().includes(term) ||
      (s.political_party && s.political_party.toLowerCase().includes(term))
    );
  });

  const displayLimit = searchTerm === '' ? 5 : 50;
  const speechesToDisplay = filteredSpeeches.slice(0, displayLimit);

  return (
    <div className="tab-content">
      <input
        type="text"
        placeholder="Αναζήτηση ομιλιών..."
        className="search-input"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      
      {loading ? <p>Φόρτωση...</p> : (
        <div className="results-grid">
          {speechesToDisplay.map((item, index) => (
            <div key={index} className="card">
              <h3>{item.member_name} <span className="party-tag">{item.political_party}</span></h3>
              <small>{item.sitting_date}</small>
              <p>{item.speech?.substring(0, 200)}...</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// 2. Component Keywords (Ανά Κόμμα)
const KeywordsTab = () => {
  const [keywordsData, setKeywordsData] = useState([]);

  useEffect(() => {
    Papa.parse('public/search_models_csv/results_keywords_by_political_party.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (result) => setKeywordsData(result.data)
    });
  }, []);

  return (
    <div className="tab-content">
      <h2>Λέξεις-Κλειδιά ανά Κόμμα</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Κόμμα</th>
              <th>Top Keywords</th>
            </tr>
          </thead>
          <tbody>
            {keywordsData.map((row, idx) => (
              <tr key={idx}>
                <td style={{fontWeight: 'bold'}}>{row.political_party}</td>
                <td>{row.top_keywords}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// 3. Component Ομοιότητας (Similarity)
const SimilarityTab = () => {
  const [pairs, setPairs] = useState([]);

  useEffect(() => {
    Papa.parse('public/similarity/top_similar_members.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (result) => setPairs(result.data)
    });
  }, []);

  return (
    <div className="tab-content">
      <h2>Ομοιότητα Βουλευτών (Cosine Similarity)</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Βουλευτής A</th>
              <th>Βουλευτής B</th>
              <th>Βαθμός Ομοιότητας</th>
            </tr>
          </thead>
          <tbody>
            {pairs.slice(0, 50).map((row, idx) => (
              <tr key={idx}>
                <td>{row['Member A']}</td>
                <td>{row['Member B']}</td>
                <td>
                  <div className="similarity-bar-container">
                    <div 
                      className="similarity-bar" 
                      style={{width: `${parseFloat(row.Similarity) * 100}%`}}
                    ></div>
                    <span>{parseFloat(row.Similarity).toFixed(4)}</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// 4. Component LSI / Clustering
const ClusteringTab = () => {
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    // Εδώ φορτώνουμε το αρχείο με τα κέντρα των clusters ή τα θέματα
    Papa.parse('public/clustering_results/cluster_topic_analysis.csv', { 
      download: true, 
      header: true, 
      skipEmptyLines: true,
      complete: (result) => setClusters(result.data) 
    });
  }, []);

  return (
    <div className="tab-content">
      <h2>Ανάλυση Θεματικών Ενοτήτων (Clustering)</h2>
      <p>Μέσος όρος βαρύτητας θεμάτων (Topics) ανά Cluster</p>
      
      <div className="clusters-grid">
        {clusters.map((cluster, idx) => (
          <div key={idx} className="cluster-card">
            <h3>Cluster {cluster.Cluster_ID}</h3>
            <ul>
              {Object.keys(cluster).map((key) => {
                if (key.startsWith('Topic_') && parseFloat(cluster[key]) > 0.05) { // Δείξε μόνο τα σημαντικά
                   return <li key={key}>{key}: {parseFloat(cluster[key]).toFixed(3)}</li>
                }
                return null;
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- ΚΥΡΙΟ APP COMPONENT ---

function App() {
  const [activeTab, setActiveTab] = useState('search');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🔍 Parliament Mining</h1>
        <p>Ανάκτηση Πληροφορίας & Ανάλυση Ομιλιών 1989-2020</p>
      </header>

      <nav className="tabs-nav">
        <button 
          className={activeTab === 'search' ? 'active' : ''} 
          onClick={() => setActiveTab('search')}
        >
          🔍 Αναζήτηση
        </button>
        <button 
          className={activeTab === 'keywords' ? 'active' : ''} 
          onClick={() => setActiveTab('keywords')}
        >
          🔑 Λέξεις Κλειδιά
        </button>
        <button 
          className={activeTab === 'similarity' ? 'active' : ''} 
          onClick={() => setActiveTab('similarity')}
        >
          🤝 Ομοιότητα Μελών
        </button>
        <button 
          className={activeTab === 'clustering' ? 'active' : ''} 
          onClick={() => setActiveTab('clustering')}
        >
          📊 Clustering / LSI
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'search' && <SearchTab />}
        {activeTab === 'keywords' && <KeywordsTab />}
        {activeTab === 'similarity' && <SimilarityTab />}
        {activeTab === 'clustering' && <ClusteringTab />}
      </main>

      <footer className="app-footer">
        <p>Χειμερινό Εξάμηνο 2025-2026 | Ανάκτηση Πληροφορίας</p>
      </footer>
    </div>
  );
}

export default App;