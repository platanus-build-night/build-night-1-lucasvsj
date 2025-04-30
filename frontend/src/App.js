import React, { useState, useEffect } from 'react';
import GameDetails from './components/GameDetails';
import LatestScrapedCarousel from './components/LatestScrapedCarousel';

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [selectedGame, setSelectedGame] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 600);
  const limit = 10;

  // Handle responsive breakpoint
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 600);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchGames = async (q, off) => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token') || '';
      const url = new URL('http://localhost:8000/games');
      url.searchParams.set('query', q);
      url.searchParams.set('ignore_case', 'true');
      url.searchParams.set('limit', limit);
      url.searchParams.set('offset', off);

      const res = await fetch(url.toString(), {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!res.ok) {
        if (res.status === 404) {
          setResults([]);
          setTotal(0);
          setError('No matching games found.');
        } else {
          throw new Error(`HTTP ${res.status}`);
        }
      } else {
        const data = await res.json();
        setResults(data.results);
        setTotal(data.total);
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setOffset(0);
    fetchGames(query, 0);
  };

  const handlePrev = () => {
    const newOffset = Math.max(offset - limit, 0);
    setOffset(newOffset);
    fetchGames(query, newOffset);
  };

  const handleNext = () => {
    if (offset + limit >= total) return;
    const newOffset = offset + limit;
    setOffset(newOffset);
    fetchGames(query, newOffset);
  };

  const renderItem = (item) => {
    const year = item.released ? new Date(item.released).getFullYear() : '';
    const score = item.metacritic;
    let pillColor = '#999';
    if (score >= 75) pillColor = '#4caf50';
    else if (score >= 50) pillColor = '#ffeb3b';
    else if (score != null) pillColor = '#f44336';

    return (
      <div
        key={item.id}
        onClick={() => setSelectedGame(item)}
        style={{
          display: 'flex',
          flexDirection: isMobile ? 'column' : 'row',
          alignItems: isMobile ? 'flex-start' : 'center',
          padding: '1rem',
          borderBottom: '1px solid #eee',
          cursor: 'pointer',
          gap: isMobile ? '0.5rem' : '1rem',
        }}
      >
        <img
          src={item.scraped_data?.image_url || 'https://via.placeholder.com/60x90?text=No+Image'}
          alt={item.name}
          style={{
            width: isMobile ? 80 : 60,
            height: isMobile ? 120 : 90,
            objectFit: 'cover',
            borderRadius: 4,
            boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
          }}
        />
        <div style={{ flex: 1 }}>
          <div
            style={{
              fontSize: isMobile ? '1rem' : '1.2rem',
              fontWeight: 600,
              marginBottom: '0.5rem',
              color: '#222',
            }}
          >
            {item.name}{' '}
            {year && <span style={{ fontWeight: 400, color: '#888' }}>({year})</span>}
          </div>

          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.75rem',
              marginBottom: '0.5rem',
              color: '#555',
              fontSize: '0.9rem',
            }}
          >
            <div>🎮 <strong>{item.scraped_data?.infobox["Platform(s)"]?.join(' || ') || item.platforms[0]?.name || 'N/A'}</strong></div>
            <div>🏷️ <strong>{item.genres[0]?.name || 'N/A'}</strong></div>
            <div>👤 <strong>{item.developers[0]?.name || item.publishers[0]?.name || 'N/A'}</strong></div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ color: '#777', fontSize: '0.9rem' }}>Metacritic:</span>
            <span
              style={{
                display: 'inline-block',
                minWidth: '40px',
                textAlign: 'center',
                fontWeight: 600,
                backgroundColor: pillColor,
                color: pillColor === '#ffeb3b' ? '#333' : '#fff',
                padding: '2px 8px',
                borderRadius: '12px',
                fontSize: '0.9rem',
                boxShadow: '0 1px 4px rgba(0,0,0,0.1)',
              }}
            >
              {score ?? 'N/A'}
            </span>
          </div>
        </div>
      </div>
    );
  };

  if (selectedGame) {
    return (
      <GameDetails
        game={selectedGame}
        onBack={() => setSelectedGame(null)}
        style={{ backgroundColor: '#fff', color: '#000' }}
      />
    );
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: '#fff',
        padding: isMobile ? '1rem' : '2rem',
        boxSizing: 'border-box',
        fontFamily: 'Arial, sans-serif',
        color: '#000',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <h1>GameGrader (GG)</h1>
      <LatestScrapedCarousel />
      <div style={{ maxWidth: isMobile ? '100%' : 600, margin: '0 auto' }}>
        <form
          onSubmit={handleSearch}
          style={{
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            gap: '0.5rem',
            marginBottom: '1rem',
          }}
        >
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search games..."
            style={{
              flex: 1,
              padding: '0.5rem',
              borderRadius: isMobile ? '4px' : '4px 0 0 4px',
              border: '1px solid #ccc',
              background: '#fff',
              color: '#000',
              fontSize: '1rem',
            }}
          />
          <button
            type="submit"
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #ccc',
              borderRadius: isMobile ? '4px' : '0 4px 4px 0',
              background: '#eee',
              color: '#000',
              cursor: 'pointer',
              fontSize: '1rem',
            }}
            disabled={loading}
          >
            {loading ? 'Searching…' : 'Search'}
          </button>
        </form>

        {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}
        {!loading && !error && results.length === 0 && query.trim() && (
          <div style={{ color: '#555', margin: '1rem 0' }}>
            No games found for "{query}".
          </div>
        )}

        {total > 0 && (
          <div style={{ color: '#000', marginBottom: '0.5rem' }}>
            Showing {offset + 1}–{Math.min(offset + limit, total)} of {total} results
          </div>
        )}

        <div>{results.map((g) => renderItem(g))}</div>

        {total > limit && (
          <div
            style={{
              display: 'flex',
              flexDirection: isMobile ? 'column' : 'row',
              justifyContent: 'space-between',
              gap: '0.5rem',
              marginTop: '1rem',
            }}
          >
            <button
              onClick={handlePrev}
              disabled={offset === 0}
              style={{ padding: '0.5rem 1rem', background: '#fff', border: '1px solid #ccc', color: '#000', flex: 1 }}
            >
              Previous
            </button>
            <button
              onClick={handleNext}
              disabled={offset + limit >= total}
              style={{ padding: '0.5rem 1rem', background: '#fff', border: '1px solid #ccc', color: '#000', flex: 1 }}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
