import React, { useState, useEffect } from 'react';
import MainLayout from './layouts/MainLayout';
import SearchBar from './components/SearchBar';
import SourceCard from './components/SourceCard';
import RelatedCard from './components/RelatedCard';
import AuthModal from './components/AuthModal';

export default function App() {

  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);


  const [sources, setSources] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [archiveSources, setArchiveSources] = useState([]); 
  const [loading, setLoading] = useState(false);
  const [historyStack, setHistoryStack] = useState([]);
  const [currentQuery, setCurrentQuery] = useState('');

  const [savedSearches, setSavedSearches] = useState([]);
  const [favorites, setFavorites] = useState([]);


  useEffect(() => {
    const savedUser = localStorage.getItem('user_profile');
    if (savedUser) {
      setCurrentUser(JSON.parse(savedUser));
    }
  }, []);

  useEffect(() => {
    if (!currentUser) {
      setSavedSearches([]);
      setFavorites([]);
      return;
    }
    fetchUserData();
  }, [currentUser]);

  const fetchUserData = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    try {
      const searchRes = await fetch(`http://127.0.0{token}`);
      const searches = await searchRes.json();
      setSavedSearches(searches || []);

      const favRes = await fetch(`http://127.0.0{token}`);
      const favs = await favRes.json();
      setFavorites(favs || []);
    } catch (err) {
      console.error("Error pulling history lists:", err);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_profile');
    setCurrentUser(null);
  };

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
 
        <div style={{ 
          display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
          background: '#fcfcfc', padding: '12px 16px', borderRadius: '6px', 
          border: '1px solid #eaeaea', marginBottom: '20px' 
        }}>
          <div>
            {currentUser ? (
              <span style={{ fontSize: '14px', color: '#333' }}>
                Signed in as: <strong>{currentUser.username}</strong> ({currentUser.email})
              </span>
            ) : (
              <span style={{ fontSize: '14px', color: '#666', fontStyle: 'italic' }}>
                Viewing as Guest Node. Sign in to capture favorites maps.
              </span>
            )}
          </div>
          <div>
            {currentUser ? (
              <button onClick={handleSignOut} style={{ background: '#333', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '13px' }}>
                Sign Out
              </button>
            ) : (
              <button onClick={() => setIsAuthOpen(true)} style={{ background: '#0070f3', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '13px', fontWeight: 'bold' }}>
                Account Sign In
              </button>
            )}
          </div>
        </div>

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
              <SourceCard key={item.entry_id} item={item} isArchive={false} />
            ))}
          </section>
        )}

        {!loading && archiveSources.length > 0 && (
          <section style={{ marginTop: '20px' }}>
            <h2 style={{ fontSize: '18px', borderBottom: '2px solid #e60000', paddingBottom: '4px', marginBottom: '14px', color: '#e60000' }}>📚 Real-Time Historical Reference Sources (Top 10)</h2>
            {archiveSources.map((doc, idx) => {
              const safeUrl = doc?.url && String(doc.url).includes('http') 
                ? String(doc.url).trim() 
                : 'https://archive.org' + encodeURIComponent(doc?.title || currentQuery || "history");

              return (
                <a 
                  href={safeUrl} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  key={idx}
                  style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
                >
                  <SourceCard item={doc} isArchive={true} />
                </a>
              );
            })}
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

      <AuthModal 
        isOpen={isAuthOpen} 
        onClose={() => setIsAuthOpen(false)} 
        onAuthSuccess={(user) => setCurrentUser(user)} 
      />
    </MainLayout>
  );
}

















