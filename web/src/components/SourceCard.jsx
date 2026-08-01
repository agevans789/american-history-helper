import React from 'react';

export default function SourceCard({ item, isArchive }) {
  const themeColor = isArchive ? '#e60000' : '#0070f3';
  const badgeText = isArchive ? 'Internet Archive Digital Resource' : item?.historical_era || 'Local Database Node';
  
  // Explicit absolute query string removes character splits
  const cleanTitle = item && item.title ? String(item.title) : 'history';
  const fallbackUrl = 'https://archive.org' + encodeURIComponent(cleanTitle);
  
  // Strict cleanup checks avoid empty objects from breaking the click loops
  const rawUrl = item && item.url ? String(item.url).trim() : '';
  const itemUrl = isArchive ? (rawUrl || fallbackUrl) : '#';

  const cardDescription = item?.description || item?.content || "No summary text provided for this archival record entry.";
  const cardTitle = item?.title || "Untitled Historical Document Artifact";

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
      <h3 style={{ margin: '0 0 6px 0' }}>
        {isArchive ? (
          <a 
            href={itemUrl} 
            target="_blank" 
            rel="noopener noreferrer" 
            style={{ color: themeColor, textDecoration: 'none', display: 'inline-block' }}
          >
            {cardTitle}
          </a>
        ) : (
          <span style={{ color: themeColor }}>{cardTitle}</span>
        )}
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
        <a 
          href={itemUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          style={{ fontSize: '12px', color: '#0070f3', fontWeight: 'bold', textDecoration: 'none', display: 'inline-block' }}
        >
          View Original Document Artifact →
        </a>
      )}
    </article>
  );
}





