import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SignIn() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await fetch('/auth/login', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) throw new Error('Invalid credentials');
      const { access_token } = await res.json();
      localStorage.setItem('token', access_token);
      navigate('/');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Sign In</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: 300 }}>
        <input type="text" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} required />
        <button type="submit">Sign In</button>
      </form>
    </div>
  );
}