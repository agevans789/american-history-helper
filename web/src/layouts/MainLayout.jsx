import React from "react";

export default function MainLayout({ children }) {
    return (
        <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto', fontFamily: 'sans-serif' }}>
            <header style={{ marginBottom: '20px', borderBottom: '1px solid #eee', paddingBottom: '10px' }}>
                <h1 style={{ margin: 0, color: '#111' }}>American History Helper</h1>
            </header>
            <div style={{ marginBottom: '20px', display: 'grid', gridTemplateColumns: '65% 35%', gap: '30px' }}>
                {children}
            </div>
        </div>
    );
}