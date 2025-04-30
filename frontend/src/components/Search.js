// src/components/Search.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Search({ onSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSearch = async e => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a search term.');
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch(
        `http://localhost:8000/games?query=${encodeURIComponent(query)}&ignore_case=true`,
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        }
      );
      if (!res.ok) throw new Error(`Status ${res.status}`);
      const data = await res.json();
      setResults(data.results);
    } catch {
      setError('Failed to fetch games.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = game => {
    onSelect(game);
    navigate(`/games/${game.id}`);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search games..."
          style={{ flex: 1, padding: '0.5rem', fontSize: '1rem' }}
        />
        <button
          type="submit"
          style={{ padding: '0.5rem 1rem', fontSize: '1rem' }}
          disabled={loading}
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}

      <ul style={{ listStyle: 'none', padding: 0, marginTop: '1rem' }}>
        {!loading && results.length === 0 && !error && (
          <li style={{ color: '#555' }}>No results yet.</li>
        )}
        {results.map(g => (
          <li
            key={g.id}
            onClick={() => handleSelect(g)}
            style={{
              cursor: 'pointer',
              padding: '0.5rem 0',
              borderBottom: '1px solid #ccc',
            }}
          >
            {g.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
