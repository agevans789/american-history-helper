import React, { useState } from 'react';

export default function SearchBar({ onSearch }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSearch(input.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '24px', display: 'flex', gap: '8px' }}>
      <input
        type="text"
        placeholder="Search American History (e.g., Abraham Lincoln)..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        style={{
          flexGrow: 1,
          padding: '12px',
          borderRadius: '6px',
          border: '1px solid #ccc',
          fontSize: '16px',
          background: '#fff',
          color: '#000'
        }}
      />
      <button 
        type="submit" 
        style={{ 
          padding: '12px 24px', 
          borderRadius: '6px', 
          backgroundColor: '#0070f3', 
          color: 'white', 
          border: 'none', 
          cursor: 'pointer',
          fontWeight: 'bold'
        }}
      >
        Search
      </button>
    </form>
  );
}

