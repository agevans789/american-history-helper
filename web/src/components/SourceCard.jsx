import React from 'react';

export default function SourceCard({ item, isLoc }) {
  // Select style theme matching either database (blue) or Library of Congress (red)
  const themeColor = isLoc ? '#e60000' : '#0070f3';
  const badgeText = isLoc ? 'Library of Congress Archive' : item.historical_era || 'Local Database';
  const itemUrl = isLoc ? item.url : '#';

  return (
    <article style={{ 
      padding: '16px', 
      border: '1px solid #eaeaea', 
      borderRadius: '8px', 
      marginBottom: '16px', 
      background: isLoc ? '#fcfcfc' : '#fff',
      boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
    }}>
      <h3 style={{ margin: '0 0 6px 0' }}>
        {isLoc ? (
          <a href={itemUrl} target="_blank" rel="noopener noreferrer" style={{ color: themeColor, textDecoration: 'none' }}>
            {item.title}
          </a>
        ) : (
          <span style={{ color: themeColor }}>{item.title}</span>
        )}
      </h3>
      
      <div style={{ marginBottom: '10px' }}>
        <span style={{ 
          fontSize: '11px', 
          background: isLoc ? '#ffebeb' : '#e6f0ff', 
          color: themeColor,
          padding: '3px 8px', 
          borderRadius: '4px',
          fontWeight: 'bold'
        }}>
          {badgeText}
        </span>
        {isLoc && <span style={{ fontSize: '11px', color: '#777', marginLeft: '10px' }}>Archival Date: {item.item_date}</span>}
      </div>

      <p style={{ color: '#444', fontSize: '14px', lineHeight: '1.5', margin: '0 0 10px 0' }}>
        {item.description || item.content}
      </p>

      {isLoc && (
        <a href={itemUrl} target="_blank" rel="noopener noreferrer" style={{ fontSize: '12px', color: '#0070f3', fontWeight: 'bold' }}>
          View Original Document Artifact →
        </a>
      )}
    </article>
  );
}
