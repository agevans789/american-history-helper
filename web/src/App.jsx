import React, { useState } from "react";
import MainLayout from "./layouts/MainLayout";
import SearchBar from "./components/SearchBar";

export default function App() {
    const [sources, setSources] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleSearch = async (queryPhrase) => {
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/search?query=${encodeURIComponent(queryPhrase)}`);
            const data = await response.json();
            setSources(data.sources || []);
            setRecommendations(data.recommendations || []);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <MainLayout>
            <main>
                <SearchBar onSearch={handleSearch} />
                {loading && <p>Loading...</p>}
                {!loading && sources.length === 0 && (
                    <p style={{ color: '#666' }}>No sources found</p>
                )}

                {sources.map((item) => (
                    <article key={item.entry_id} style={{ marginBottom: '16px', padding: '16px', border: '1px solid #eaeaea', borderRadius: '8px' }}>
                        <h3 style={{ margin: '0 0 8px 0', color: '#0070f3' }}>{item.title}</h3>
                        <span style={{ fontSize: '12px', background: '#eee', padding: '2px 6px', borderRadius: '4px' }}>{item.historical_era}</span>
                        <p style={{ lineHeight: '1.5', color: '#444' }}>{item.content}</p>
                    </article>
                ))}
            </main>

            <aside style={{ borderLeft: '1px solid #eee', paddingLeft: '20px' }}>
                <h2 style={{ fontSize: '20px', margin: '0 0 16px 0', color: '#333' }}>Related Topics Graph</h2>
                
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
    )
}