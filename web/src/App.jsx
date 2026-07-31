import React, { useState } from 'react';
import MainLayout from './layouts/MainLayout';
import SearchBar from './components/SearchBar';

export default function App() {
  const [sources, setSources] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [locSources, setLocSources] = useState([]); 
  const [loading, setLoading] = useState(false);

  const handleSearch = async (queryPhrase) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/discover?q=${encodeURIComponent(queryPhrase)}`);
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
        
        {loading && <p>Searching the historical database archives...</p>}

        {!loading && sources.length > 0 && (
          <section>
            <h2 style={{ fontSize: '20px', borderBottom: '2px solid #0070f3', paddingBottom: '4px' }}>Local History Entries</h2>
            {sources.map((item) => (
              <article key={item.entry_id} style={{ padding: '16px', border: '1px solid #eaeaea', borderRadius: '8px', marginBottom: '16px', background: '#fff' }}>
                <h3 style={{ margin: '0 0 8px 0', color: '#0070f3' }}>{item.title}</h3>
                <span style={{ fontSize: '12px', background: '#eee', padding: '2px 6px', borderRadius: '4px' }}>{item.historical_era}</span>
                <p style={{ color: '#444', lineHeight: '1.5' }}>{item.content}</p>
              </article>
            ))}
          </section>
        )}

    
        {!loading && locSources.length > 0 && (
          <section style={{ marginTop: '30px' }}>
            <h2 style={{ fontSize: '20px', borderBottom: '2px solid #e60000', paddingBottom: '4px' }}>📚 Library of Congress Primary Sources</h2>
            {locSources.map((doc, idx) => (
              <article key={idx} style={{ padding: '16px', border: '1px solid #eaeaea', borderRadius: '8px', marginBottom: '16px', background: '#fcfcfc' }}>
                <h3 style={{ margin: '0 0 4px 0' }}>
                  <a href={doc.url} target="_blank" rel="noopener noreferrer" style={{ color: '#e60000', textDecoration: 'none' }}>
                    {doc.title}
                  </a>
                </h3>
                <span style={{ fontSize: '11px', color: '#777' }}>Archival Date: {doc.item_date || 'Unknown'}</span>
                <p style={{ color: '#555', fontSize: '14px', marginTop: '8px', lineHeight: '1.4' }}>{doc.description}</p>
                <a href={doc.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '12px', color: '#0070f3' }}>
                  View Original Document Artifact →
                </a>
              </article>
            ))}
          </section>
        )}

        {!loading && sources.length === 0 && locSources.length === 0 && (
          <p style={{ color: '#666' }}>Type a historical topic above to search the digital archives.</p>
        )}
      </main>

    
      <aside style={{ borderLeft: '1px solid #eee', paddingLeft: '20px' }}>
        <h2 style={{ fontSize: '20px', margin: '0 0 16px 0', color: '#333' }}>🧭 Related Topics Graph</h2>
        
        {recommendations.length === 0 && <p style={{ color: '#999', fontSize: '14px' }}>No graph connections active. Connect to database to generate map paths.</p>}
        
        {recommendations.map((topic) => (
          <div 
            key={topic.entry_id} 
            onClick={() => handleSearch(topic.title)} 
            style={{ 
              padding: '12px', 
              background: '#f9f9f9', 
              borderRadius: '6px', 
              marginBottom: '12px', 
              cursor: 'pointer',
              border: '1px solid #eee'
            }}
          >
            <h4 style={{ margin: '0 0 4px 0', color: '#111' }}>{topic.title}</h4>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#666' }}>
              <span>Connection: <strong>{topic.relationship_type || 'General'}</strong></span>
              <span>Weight: {topic.weight}</span>
            </div>
          </div>
        ))}
      </aside>
    </MainLayout>
  );
}
