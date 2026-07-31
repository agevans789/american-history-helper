import React, { useState } from "react";

export default function SearchBar({ onSearch }) {
    const [input, setInput] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim()) onSearch(input);
    };

    return (
        <form onSubmit={handleSubmit} style={{ marginBottom: '24px', display: 'flex', gap: '8px' }}>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Search..."
                style={{ 
                    flexGrow: 1, 
                    padding: '12px', 
                    borderRadius: '6px',
                    border: '1px solid #ccc',
                    fontSize: '16px' 
                }}
            />
            <button
                type="submit"
                style={{
                    padding: '12px 24px',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: '#0070f3',
                    color: '#fff',
                    fontSize: '16px',
                    cursor: 'pointer'
                }}
            >
                Search
            </button>
        </form>
    );
}