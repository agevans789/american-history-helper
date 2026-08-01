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
  
  const [historyStack, setHistoryStack] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');

  const handleSearch = async (queryPhrase, isGoingBack = false) => {
    if (!queryPhrase || queryPhrase.trim() === '') return;
    setLoading(true);
    
    try {
      const titleCaseQuery = queryPhrase.trim().split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(' ');

      const targetUrl = 'http://127.0.0' + encodeURIComponent(queryPhrase);
      const response = await fetch(targetUrl);
      const backendData = await response.json();
      setSources(backendData.matching_sources || []);
      const era = backendData.matching_sources[0]?.historical_era || 'American History Archive';

      const searchUrl = `https://wikipedia.org{encodeURIComponent(queryPhrase + " history documentation")}&srlimit=10&format=json&origin=*`;
      const searchResponse = await fetch(searchUrl);
      const searchData = await searchResponse.json();
      const results = searchData.query?.search || [];
      
      const parsedDocs = results.map((item) => {
        const cleanSnippet = item.snippet.replace(/<[^>]*>/g, '');
        return {
          title: item.title,
          url: `https://wikipedia.org{item.title.replace(/ /g, '_')}`,
          item_date: "Archival Record",
          description: cleanSnippet ? cleanSnippet + "..." : "Historical archive documentation record entry details."
        };
      });
      setLocSources(parsedDocs);

      const graphUrl = `https://wikipedia.org{encodeURIComponent(titleCaseQuery)}&plnamespace=0&pllimit=40&format=json&redirects=1&origin=*`;
      const graphResponse = await fetch(graphUrl);
      const graphData = await graphResponse.json();
      
      const pages = graphData.query?.pages || {};
      const parsedLinks = [];
      const genericStops = new Set([
        "united states", "library of congress", "federal government", "washington, d.c.", 
        "wikipedia", "wayback machine", "doi (identifier)", "isbn (identifier)", "national archives",
        "american history", "politician", "legislation", "treaty", "united kingdom", "great britain",
        "president of the united states", "house of representatives"
      ]);

      for (const pageId in pages) {
        const rawLinks = pages[pageId].links || [];
        for (const link of rawLinks) {
          const nodeTitle = link.title;
          if (
            nodeTitle.toLowerCase() !== queryPhrase.toLowerCase() &&
            !genericStops.has(nodeTitle.toLowerCase()) &&
            !/\d/.test(nodeTitle) &&
            nodeTitle.length > 3
          ) {
            const idx = parsedLinks.length;
            const relCategories = ["Contextual Connection", "Historical Contributor", "Chronological Link", "Socio-Political Theme"];
            parsedLinks.push({
              entry_id: 2000 + idx,
              title: nodeTitle,
              historical_era: era,
              relationship_type: relCategories[idx % relCategories.length],
              weight: parseFloat((0.96 - (idx * 0.04)).toFixed(2))
            });
            if (parsedLinks.length >= 4) break;
          }
        }
        if (parsedLinks.length >= 4) break;
      }

      // Context fallbacks if a rare name yields no immediate graph links
      if (parsedLinks.length === 0) {
        const fallbacks = [titleCaseQuery + " Biographies", "Political Context", "Socio-Cultural Legacy", "Historical Timeline"];
        fallbacks.forEach((title, idx) => {
          parsedLinks.push({
            entry_id: 2001 + idx,
            title: title,
            historical_era: era,
            relationship_type: "Contextual Connection",
            weight: parseFloat((0.95 - (idx * 0.05)).toFixed(2))
          });
        });
      }
      setRecommendations(parsedLinks);

      if (!isGoingBack && currentQuery) {
        setHistoryStack((prev) => [...prev, currentQuery]);
      }
      setCurrentQuery(queryPhrase);
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
        
        {/* Navigation Toolbar */}
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

        {!loading && locSources.length > 0 && (
          <section style={{ marginTop: '20px' }}>
            <h2 style={{ fontSize: '18px', borderBottom: '2px solid #e60000', paddingBottom: '4px', marginBottom: '14px', color: '#e60000' }}>📚 Real-Time Historical Reference Sources (Top 10)</h2>
            {locSources.map((doc, idx) => (
              <SourceCard key={idx} item={doc} isLoc={true} />
            ))}
          </section>
        )}

        {!loading && sources.length === 0 && locSources.length === 0 && (
          <p style={{ color: '#666', background: '#f5f5f5', padding: '30px', borderRadius: '6px', textAlign: 'center', marginTop: '20px' }}>
            Type a historical event above to explore the discovery networks map.
          </p>
        )}
      </main>

      <aside style={{ borderLeft: '1px solid #eee', paddingLeft: '20px', minWidth: '260px' }}>
        <h2 style={{ fontSize: '18px', margin: '0 0 16px 0', color: '#333' }}>🧭 Related Topics Graph</h2>
        
        {recommendations.length === 0 && (
          <p style={{ color: '#999', fontSize: '13px', fontStyle: 'italic' }}>
            No graph connections active. Connect and seed your local database to map discovery paths.
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



