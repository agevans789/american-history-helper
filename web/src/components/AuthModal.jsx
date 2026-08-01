import React, { useState } from 'react';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  if (!isOpen) return null;

  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';
    const payload = isRegister ? { username, email, password } : { username, password };

    try {
      const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication routing loop failed.');
      }

      if (isRegister) {
        // Automatically switch to sign-in phase on registration success
        setIsRegister(false);
        setErrorMsg('Account built! Please enter credentials to sign in.');
      } else {
        // Save the session parameters securely inside the local browser storage
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('user_profile', JSON.stringify(data.user));
        onAuthSuccess(data.user);
        onClose();
      }
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center',
      justifyContent: 'center', zIndex: 1000, pointerEvents: 'auto'
    }}>
      <div style={{ background: '#fff', padding: '30px', borderRadius: '8px', minWidth: '320px', textAlign: 'left' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>{isRegister ? 'Create Profile Account' : 'Sign In'}</h2>
        
        {errorMsg && <p style={{ color: '#e60000', fontSize: '13px', background: '#ffebeb', padding: '8px', borderRadius: '4px' }}>{errorMsg}</p>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <label style={{ fontSize: '13px', fontWeight: 'bold' }}>Username</label>
          <input type="text" value={username} onChange={e => setUsername(e.target.value)} required style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />

          {isRegister && (
            <>
              <label style={{ fontSize: '13px', fontWeight: 'bold' }}>Email Address</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />
            </>
          )}

          <label style={{ fontSize: '13px', fontWeight: 'bold' }}>Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }} />

          <button type="submit" style={{ background: '#0070f3', color: '#fff', padding: '10px', border: 'none', borderRadius: '4px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' }}>
            {isRegister ? 'Register Node Account' : 'Authenticate Profile'}
          </button>
        </form>

        <button onClick={() => setIsRegister(!isRegister)} style={{ background: 'none', border: 'none', color: '#0070f3', cursor: 'pointer', fontSize: '13px', marginTop: '14px', padding: 0 }}>
          {isRegister ? 'Already have an account? Sign In' : 'Need an investigative account? Register'}
        </button>

        <button onClick={onClose} style={{ background: '#eee', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', float: 'right', marginTop: '14px' }}>
          Cancel
        </button>
      </div>
    </div>
  );
}
