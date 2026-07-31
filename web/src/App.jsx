import React, { useState } from 'react';
import MainLayout from './layouts/MainLayout';
import SearchBar from './components/SearchBar';
import SourceCard from './components/SourceCard';
import RelatedCard from './components/RelatedCard';

export default function App() {
  const [sources, setSources] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [locSources, setLocSources] = useState([]); 
  const [loading, setLoading] = useState(false);

  const handleSearch = async (queryPhrase) => {
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/discover?q=${encodeURIComponent(queryPhrase)}`);
      const data = await response.json();
      
      setSources(data.matching_sources || []);
      setRecommendations(data.recommended_topics || []);
      setLocSources(data.loc_primary_sources || []); 
    } catch (error) {
      console.error("Error communicating with history API:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <main>
        <SearchBar onSearch={handleSearch} />
        
        {loading && <p style={{ color: '#666', fontStyle: 'italic' }}>Searching the historical database archives...</p>}
 
        {!loading && sources.length > 0 && (
          <section style={{ marginBottom: '24px' }}>
            <h2 style={{ fontSize: '18px', borderBottom: '2px solid #0070f3', paddingBottom: '4px', marginBottom: '14px' }}>Local History Entries</h2>
            {sources.map((item) => (
              <SourceCard key={item.entry_id} item={item} isLoc={false} />
            ))}
          </section>
        )}

        {!loading && locSources.length > 0 && (
          <section>
            <h2 style={{ fontSize: '18px', borderBottom: '2px solid #e60000', paddingBottom: '4px', marginBottom: '14px' }}>📚 Library of Congress Primary Sources</h2>
            {locSources.map((doc, idx) => (
              <SourceCard key={idx} item={doc} isLoc={true} />
            ))}
          </section>
        )}

        {!loading && sources.length === 0 && locSources.length === 0 && (
          <p style={{ color: '#666', background: '#f5f5f5', padding: '20px', borderRadius: '6px', textAlign: 'center' }}>
            Type a historical event above to explore the discovery networks map.
          </p>
        )}
      </main>

      <aside style={{ borderLeft: '1px solid #eee', paddingLeft: '20px' }}>
        <h2 style={{ fontSize: '18px', margin: '0 0 16px 0', color: '#333' }}>Related Topics Graph</h2>
        
        {recommendations.length === 0 && (
          <p style={{ color: '#999', fontSize: '13px', fontStyle: 'italic' }}>
            No graph connections active. Connect and seed your local database to map discovery paths.
          </p>
        )}
        
        {recommendations.map((topic) => (
          <RelatedCard key={topic.entry_id} topic={topic} onClick={handleSearch} />
        ))}
      </aside>
    </MainLayout>
  );
}

