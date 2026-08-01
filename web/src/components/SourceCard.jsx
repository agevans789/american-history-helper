import React from 'react';

export default function SourceCard({ item, isArchive }) {
  const themeColor = isArchive ? '#e60000' : '#0070f3';
  const badgeText = isArchive ? 'Internet Archive Digital Resource' : item?.historical_era || 'Local Database Node';

  const cardDescription = item?.description || item?.content || "No summary text provided for this archival record entry.";
  const cardTitle = item?.title || "Untitled Historical Document Artifact";

  const [isStarred, setIsStarred] = useState(false);

  const handleFavoriteClick = async (e) => {
    e.preventDefault(); 
    e.stopPropagation();
    
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    try {
      const response = await fetch(`http://127.0.0{token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: cardTitle,
          url: item?.url || 'https://archive.org',
          description: cardDescription
        })
      });

      if (response.ok) {
        setIsStarred(true);
      }
    } catch (err) {
      console.error("Failed to commit favorite row state:", err);
    }
  };

  return (
    <article style={{ 
      padding: '16px', 
      border: '1px solid #eaeaea', 
      borderRadius: '8px', 
      marginBottom: '16px', 
      background: isArchive ? '#fcfcfc' : '#fff',
      boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
      textAlign: 'left'
    }}>
      {isArchive && isUserLoggedIn && (
        <button 
          onClick={handleFavoriteClick}
          style={{
            position: 'absolute', top: '16px', right: '16px', background: 'none',
            border: 'none', fontSize: '20px', cursor: 'pointer', padding: 0,
            color: isStarred ? '#ffc107' : '#ccc', filter: 'drop-shadow(0 1px 1px rgba(0,0,0,0.05))'
          }}
          title={isStarred ? "Favorited Source" : "Save to Favorites"}
        >
          {isStarred ? '★' : '☆'}
        </button>
      )}
      <h3 style={{ margin: '0 0 6px 0', color: themeColor }}>
        {cardTitle}
      </h3>
      
      <div style={{ marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ 
          fontSize: '11px', 
          background: isArchive ? '#ffebeb' : '#e6f0ff', 
          color: themeColor,
          padding: '3px 8px', 
          borderRadius: '4px',
          fontWeight: 'bold'
        }}>
          {badgeText}
        </span>
        {isArchive && item?.item_date && (
          <span style={{ fontSize: '11px', color: '#777' }}>
            Archival Date: {item.item_date}
          </span>
        )}
      </div>

      <p style={{ color: '#444', fontSize: '14px', lineHeight: '1.5', margin: '0 0 10px 0' }}>
        {cardDescription}
      </p>

      {isArchive && (
        <span style={{ fontSize: '12px', color: '#0070f3', fontWeight: 'bold' }}>
          View Original Document Artifact →
        </span>
      )}
    </article>
  );
}







