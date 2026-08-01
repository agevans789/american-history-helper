import React, { useState } from 'react';
import MainLayout from './layouts/MainLayout';
import SearchBar from './components/SearchBar';
import SourceCard from './components/SourceCard';
import RelatedCard from './components/RelatedCard';

export default function App() {
  const [sources, setSources] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [archiveSources, setArchiveSources] = useState([]); 
  const [loading, setLoading] = useState(false);
  
  const [historyStack, setHistoryStack] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');

  const handleSearch = async (queryPhrase, isGoingBack = false) => {
    if (!queryPhrase || queryPhrase.trim() === '') return;
    setLoading(true);
    
    try {
      const cleanTerm = queryPhrase.trim();
      const targetUrl = 'http://' + '127.0.0.1' + ':' + '8000' + '/api/discover?q=' + encodeURIComponent(cleanTerm);
      const response = await fetch(targetUrl);
      const data = await response.json();
      
      setSources(data.matching_sources || []);
      setRecommendations(data.recommended_topics || []);
      setArchiveSources(data.archive_primary_sources || []); 
      
      if (!isGoingBack && currentQuery) {
        setHistoryStack((prev) => [...prev, currentQuery]);
      }
      setCurrentQuery(cleanTerm);
    } catch (error) {
      console.error("Error communicating with data APIs:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    if (historyStack.length === 0) return;
    const previousQuery = historyStack[historyStack.length - 1];
    setHistoryStack((prev) => prev.slice(0, -1));
    handleSearch(previousQuery, true);
  };

  return (
    <MainLayout>
      <main style={{ padding: '20px', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '20px' }}>
          {historyStack.length > 0 && (
            <button 
              onClick={handleGoBack}
              style={{
                background: '#333', color: '#fff', border: 'none', padding: '8px 16px',
                borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', fontSize: '13px'
              }}
            >
              ← Go Back to '{historyStack[historyStack.length - 1]}'
            </button>
          )}
          {currentQuery && (
            <span style={{ color: '#666', fontSize: '14px', fontStyle: 'italic' }}>
              Currently Viewing: <strong>{currentQuery}</strong>
            </span>
          )}
        </div>

        <SearchBar onSearch={handleSearch} />
        
        {loading && <p style={{ color: '#666', fontStyle: 'italic', margin: '20px 0' }}>Searching the historical database archives...</p>}
 
        {!loading && sources.length > 0 && (
          <section style={{ marginBottom: '30px' }}>
            <h2 style={{ fontSize: '18px', borderBottom: '2px solid #0070f3', paddingBottom: '4px', marginBottom: '14px', color: '#0070f3' }}>Local History Entries</h2>
            {sources.map((item) => (
              <SourceCard key={item.entry_id} item={item} isLoc={false} />
            ))}
          </section>
        )}

        {!loading && archiveSources.length > 0 && (
          <section style={{ marginTop: '20px' }}>
            <h2 style={{ fontSize: '18px', borderBottom: '2px solid #e60000', paddingBottom: '4px', marginBottom: '14px', color: '#e60000' }}>📚 Real-Time Historical Reference Sources (Top 10)</h2>
            {archiveSources.map((doc, idx) => (
              <SourceCard key={idx} item={doc} isArchive={true} />
            ))}
          </section>
        )}


        {!loading && sources.length === 0 && archiveSources.length === 0 && (
          <p style={{ color: '#666', background: '#f5f5f5', padding: '30px', borderRadius: '6px', textAlign: 'center', marginTop: '20px' }}>
            Type a historical event above to explore the discovery networks map.
          </p>
        )}
      </main>

      <aside style={{ borderLeft: '1px solid #eee', paddingLeft: '20px', minWidth: '260px' }}>
        <h2 style={{ fontSize: '18px', margin: '0 0 16px 0', color: '#333' }}>🧭 Related Topics</h2>
        
        {recommendations.length === 0 && (
          <p style={{ color: '#999', fontSize: '13px', fontStyle: 'italic' }}>
            No related connections active. Connect and seed your local database to map discovery paths.
          </p>
        )}
        
        {recommendations.map((topic) => (
          <RelatedCard 
            key={topic.entry_id} 
            topic={topic} 
            onClick={() => handleSearch(topic.title)} 
          />
        ))}
      </aside>
    </MainLayout>
  );
}















