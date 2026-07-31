import React from 'react';

export default function RelatedCard({ topic, onClick }) {
  return (
    <div 
      onClick={() => onClick(topic.title)} 
      style={{ 
        padding: '12px', 
        background: '#f9f9f9', 
        borderRadius: '6px', 
        marginBottom: '12px', 
        cursor: 'pointer',
        border: '1px solid #eee',
        transition: 'background 0.2s ease'
      }}
      onMouseEnter={(e) => e.currentTarget.style.background = '#f0f0f0'}
      onMouseLeave={(e) => e.currentTarget.style.background = '#f9f9f9'}
    >
      <h4 style={{ margin: '0 0 4px 0', color: '#111' }}>{topic.title}</h4>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#666' }}>
        <span>Connection: <strong style={{ color: '#333' }}>{topic.relationship_type || 'General'}</strong></span>
        <span>Weight: {topic.weight}</span>
      </div>
    </div>
  );
}
