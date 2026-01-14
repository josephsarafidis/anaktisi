import { useState, useEffect } from 'react'
import Papa from 'papaparse'
import './App.css'

function App() {
  const [data, setData] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const csvFileName = '/Greek_Parliament_Proceedings_1989_2020_DataSample.csv';

    Papa.parse(csvFileName, {
      download: true, 
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        console.log("Φορτώθηκαν:", result.data);
        setData(result.data);
        setLoading(false);
      },
      error: (error) => {
        console.error("Σφάλμα:", error);
        setLoading(false);
      }
    });
  }, []);

  const filteredSpeeches = data.filter(s => {
    if (!s.member_name || !s.speech) return false;
    
    const nameMatch = s.member_name.toLowerCase().includes(searchTerm.toLowerCase());
    const speechMatch = s.speech.toLowerCase().includes(searchTerm.toLowerCase());
    const partyMatch = s.political_party ? s.political_party.toLowerCase().includes(searchTerm.toLowerCase()) : false;

    return nameMatch.upper || speechMatch || partyMatch;
  });

  return (
    <div className="app-container">
      <h1>Parliament Search</h1>
      <h2>Αναζήτηση Ομιλιών στη Βουλή</h2>
      
      <div className="search-container">
        <input 
          type="text" 
          placeholder="Αναζήτηση..." 
          className="search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="results-container">
        {loading ? (
          <div className="loading-spinner">Φόρτωση δεδομένων CSV...</div>
        ) : (
          <>
            <p style={{textAlign: 'left', color: '#666'}}>
               Βρέθηκαν: {filteredSpeeches.length} αποτελέσματα
            </p>

            <div className="results-grid">
              {filteredSpeeches.slice(0, 100).map((item, index) => (
                <div key={index} className="card">
                  <div style={{marginBottom: '10px'}}>
                    <h3 className="speaker-name">{item.member_name}</h3>
                    <div style={{fontSize: '0.9rem', color: '#555'}}>
                      <span style={{fontWeight: 'bold', color: '#0056b3'}}>
                        {item.political_party}
                      </span>
                    </div>
                  </div>

                  <div className="speech-date">
                    📅 {item.sitting_date} | 📍 {item.member_region}
                  </div>
                  
                  <p style={{textAlign: 'justify'}}>
                    {item.speech?.substring(0, 250)}...
                  </p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App