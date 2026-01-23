import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import './App.css';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';


// Search Component (connected with PYTHON API) 
const SearchTab = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault(); 
    
    if (!searchTerm.trim()) return;

    setLoading(true);
    setError(null);
    setResults([]);

    try {
      // Python API
      const response = await fetch('http://127.0.0.1:8000/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          query: searchTerm, 
          top_k: 20  // Show 20 most relative results
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results);
      setHasSearched(true);

    } catch (err) {
      console.error("Σφάλμα σύνδεσης με το API:", err);
      setError("Δεν ήταν δυνατή η σύνδεση με τον server. Βεβαιώσου ότι το 'main.py' τρέχει.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <form onSubmit={handleSearch} className="search-container" style={{marginBottom: '20px',width: "50%", margin: "0 auto"}}>
        <input
          type="text"
          placeholder="Αναζήτηση (π.χ. 'οικονομική κρίση', 'υγεία')..."
          className="search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{padding: '10px', width: '300px', marginRight: '10px'}}
        />
        <button 
          type="submit" 
          disabled={loading}
          style={{padding: '10px 20px', cursor: 'pointer'}}
        >
          {loading ? 'Αναζήτηση...' : '🔍 Αναζήτηση'}
        </button>
      </form>
      
      {error && <p style={{color: 'red'}}>{error}</p>}
      
      {!loading && hasSearched && results.length === 0 && (
        <p>Δεν βρέθηκαν αποτελέσματα για αυτό το query.</p>
      )}

      <div className="results-grid">
        {results.map((item, index) => (
          <div key={index} className="card">
            <h3>{item.member_name} <span className="party-tag">{item.political_party}</span></h3>
            <small>{item.sitting_date} | Relevance Score: {item.score}</small>
            <hr/>
            <p style={{fontStyle: 'italic'}}>"{item.speech_snippet}"</p>
            <button 
                onClick={() => alert(item.full_speech)}
                style={{marginTop: '10px', fontSize: '0.8rem', cursor: 'pointer'}}
            >
                Διαβάστε όλη την ομιλία
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Component Keywords (for each parliament party) 
const KeywordsTab = () => {
  const [keywordsData, setKeywordsData] = useState([]);

  useEffect(() => {
    Papa.parse('search_models_csv/results_keywords_by_political_party.csv', {
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

// Component Keywords (for each parliament member) - with search bar
const KeywordsMemberTab = () => {
  const [allData, setAllData] = useState([]); 
  const [searchInput, setSearchInput] = useState(''); 
  const [filteredData, setFilteredData] = useState([]); 
  const [hasSearched, setHasSearched] = useState(false); 

  useEffect(() => {
    Papa.parse('search_models_csv/results_keywords_by_member_name.csv', {
      download: true,
      header: true,
      skipEmptyLines: true,
      complete: (result) => setAllData(result.data)
    });
  }, []);


  const normalizeText = (text) => {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "");
  };

  const handleSearchClick = (e) => {
    e.preventDefault(); 
    
    if (!searchInput.trim()) {
        setFilteredData([]);
        setHasSearched(false);
        return;
    }

    const searchTerms = normalizeText(searchInput).split(" ").filter(t => t.length > 0);

    const results = allData.filter(row => {
        if (!row.member_name) return false;
        const memberNameNormalized = normalizeText(row.member_name);
        return searchTerms.every(term => memberNameNormalized.includes(term));
    });

    setFilteredData(results);
    setHasSearched(true);
  };

  return (
    <div className="tab-content">
      <h2>Λέξεις-Κλειδιά ανά Βουλευτή</h2>
      
      <form onSubmit={handleSearchClick} className="search-container" style={{marginBottom: '20px'}}>
        <input
          type="text"
          placeholder="Πληκτρολογήστε όνομα (π.χ. Κυριάκος Μητσοτάκης)..."
          className="search-input"
          style={{padding: '10px', width: '300px', marginRight: '10px'}}
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        <button 
          type="submit" 
          style={{padding: '10px 20px', cursor: 'pointer'}}
        >
          🔍 Αναζήτηση Βουλευτή
        </button>
      </form>

      <div className="table-container">
        {/* Μήνυμα αν δεν έχει πατηθεί αναζήτηση */}
        {!hasSearched && <p>Πληκτρολογήστε όνομα και πατήστε Αναζήτηση.</p>}
        
        {/* Μήνυμα αν πατήθηκε αλλά δεν βρέθηκε τίποτα */}
        {hasSearched && filteredData.length === 0 && (
            <p>Δεν βρέθηκε βουλευτής με αυτά τα στοιχεία.</p>
        )}

        {/* Πίνακας Αποτελεσμάτων */}
        {filteredData.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Βουλευτής</th>
                <th>Top Keywords</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((row, idx) => (
                <tr key={idx}>
                  <td style={{fontWeight: 'bold'}}>{row.member_name}</td>
                  <td>{row.top_keywords}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};


// Component Trends (Graph for usage of word over the years) 
const TrendsByYearTab = () => {
  const [word, setWord] = useState('');
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchedToken, setSearchedToken] = useState('');

  const fetchTrend = async (e) => {
    e.preventDefault();
    if (!word.trim()) return;

    setLoading(true);
    setTrendData([]);

    try {
      const response = await fetch('http://127.0.0.1:8000/trend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: word }),
      });

      const res = await response.json();
      setTrendData(res.data);
      setSearchedToken(res.token || word);
      
    } catch (err) {
      console.error("Error fetching trend:", err);
      alert("Error connecting to API");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tab-content">
      <h2>Διαχρονική Εξέλιξη Λέξης</h2>
      <p>Δείτε πώς αλλάζει η χρήση και η σημαντικότητα μιας έννοιας μέσα στα χρόνια.</p>

      <form onSubmit={fetchTrend} className="search-container" style={{marginBottom: '30px'}}>
        <input 
          type="text" 
          placeholder="Γράψτε μια λέξη (π.χ. Μακεδονία, μνημόνιο, ευρώ)..." 
          value={word}
          onChange={(e) => setWord(e.target.value)}
          className="search-input"
          style={{padding: '10px', width: '300px'}}
        />
        <button type="submit" disabled={loading} style={{marginLeft: '10px', padding: '10px 20px', cursor:'pointer'}}>
            {loading ? 'Υπολογισμός...' : 'Προβολή Γραφήματος'}
        </button>
      </form>

      {trendData.length > 0 ? (
        <div 
          style={{ 
            width: '100%', 
            height: 400, 
            background: '#fff', 
            padding: '20px', 
            borderRadius: '8px', 
            boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
            marginBottom: '60px'  
          }}
        >
          <h3 style={{textAlign: 'center', color: '#333'}}>
            Trend για τη ρίζα: <span style={{color: '#007bff'}}>"{searchedToken}"</span>
          </h3>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart 
              data={trendData} 
              margin={{ top: 5, right: 30, left: 20, bottom: 50 }} 
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => value.toFixed(2)} labelFormatter={(label) => `Έτος: ${label}`} />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#8884d8" 
                strokeWidth={3} 
                dot={{ r: 4 }} 
                activeDot={{ r: 8 }} 
                name="TF-IDF Score"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        !loading && searchedToken && <p>Δεν βρέθηκαν δεδομένα για τη λέξη "{searchedToken}". Δοκιμάστε άλλη.</p>
      )}
    </div>
  );
};

// Component Similarity
const SimilarityTab = () => {
  const [pairs, setPairs] = useState([]);

  useEffect(() => {
    Papa.parse('similarity/top_similar_members.csv', {
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

// Component LSI / Clustering 
const ClusteringTab = () => {
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    Papa.parse('clustering_results/cluster_topic_analysis.csv', { 
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
                if (key.startsWith('Topic_') && parseFloat(cluster[key]) > 0.05) {
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

// MAIN APP COMPONENT ---

function App() {
  const [activeTab, setActiveTab] = useState('search');

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Parliament Mining</h1>
        <p>Ανάκτηση Πληροφορίας & Ανάλυση Ομιλιών 1989-2020</p>
      </header>

      <nav className="tabs-nav">
        <button 
          className={activeTab === 'search' ? 'active' : ''} 
          onClick={() => setActiveTab('search')}
        >
          Αναζήτηση
        </button>
        <button 
          className={activeTab === 'keywords' ? 'active' : ''} 
          onClick={() => setActiveTab('keywords')}
        >
          Λέξεις Κλειδιά ανά Κόμμα
        </button>
        <button 
          className={activeTab === 'keywords-member' ? 'active' : ''} 
          onClick={() => setActiveTab('keywords-member')}
        >
          Λέξεις Κλειδιά ανά Βουλευτή
        </button>
        <button 
          className={activeTab === 'keywords-year' ? 'active' : ''} 
          onClick={() => setActiveTab('keywords-year')}
        >
          Συχνότητα λέξης ανά Χρονιά
        </button>
        <button 
          className={activeTab === 'similarity' ? 'active' : ''} 
          onClick={() => setActiveTab('similarity')}
        >
          Ομοιότητα Μελών
        </button>
        <button 
          className={activeTab === 'clustering' ? 'active' : ''} 
          onClick={() => setActiveTab('clustering')}
        >
          Clustering / LSI
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'search' && <SearchTab />}
        {activeTab === 'keywords' && <KeywordsTab />}
        {activeTab === 'keywords-member' && <KeywordsMemberTab />}
        {activeTab === 'keywords-year' && <TrendsByYearTab />}
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