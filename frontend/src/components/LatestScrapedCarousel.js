// src/components/LatestScrapedCarousel.jsx
import React, { useState, useEffect } from 'react';

export default function LatestScrapedCarousel() {
  const [games, setGames] = useState([]);
  const [idx, setIdx] = useState(0);
  const [touchStartX, setTouchStartX] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('http://localhost:8000/games/latest-scraped?limit=10');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const { results } = await res.json();
        setGames(results);
      } catch (e) {
        console.error('Failed to load latest scraped games:', e);
      }
    })();
  }, []);

  const prev = () => setIdx(i => Math.max(i - 1, 0));
  const next = () => setIdx(i => Math.min(i + 1, games.length - 1));

  const handleTouchStart = (e) => {
    setTouchStartX(e.touches[0].clientX);
  };
  const handleTouchEnd = (e) => {
    if (touchStartX === null) return;
    const diff = touchStartX - e.changedTouches[0].clientX;
    if (diff > 50) next();
    else if (diff < -50) prev();
    setTouchStartX(null);
  };

  if (!games.length) {
    return (
      <div style={{
        padding: '2rem',
        textAlign: 'center',
        color: '#555',
        fontSize: '1rem'
      }}>
        Loading latest games…
      </div>
    );
  }

  const game = games[idx];
  const img = game.scraped_data.image_url;
  const desc = game.scraped_data.first_paragraph;

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      maxWidth: 600,
      margin: '2rem auto',
      overflow: 'hidden',
      borderRadius: 8,
      background: '#fff',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <button
        onClick={prev}
        disabled={idx === 0}
        style={{
          position: 'absolute',
          left: 10,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 2,
          width: 40,
          height: 40,
          borderRadius: '50%',
          border: 'none',
          background: 'rgba(0,0,0,0.4)',
          color: '#fff',
          fontSize: 24,
          opacity: idx === 0 ? 0.3 : 1,
          cursor: 'pointer',
        }}
      >‹</button>

      <button
        onClick={next}
        disabled={idx === games.length - 1}
        style={{
          position: 'absolute',
          right: 10,
          top: '50%',
          transform: 'translateY(-50%)',
          zIndex: 2,
          width: 40,
          height: 40,
          borderRadius: '50%',
          border: 'none',
          background: 'rgba(0,0,0,0.4)',
          color: '#fff',
          fontSize: 24,
          opacity: idx === games.length - 1 ? 0.3 : 1,
          cursor: 'pointer',
        }}
      >›</button>

      <div
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        style={{
          display: 'flex',
          transition: 'transform 0.4s ease',
          transform: `translateX(-${idx * 100}%)`
        }}
      >
        {games.map((g) => (
          <div
            key={g.id}
            style={{
              minWidth: '100%',
              boxSizing: 'border-box',
              padding: '1rem',
              textAlign: 'center',
              height: '32rem',
            }}
          >
            {img && (
              <img
                src={g.scraped_data.image_url}
                alt={g.name}
                style={{
                  width: '100%',
                  height: 'auto',
                  maxHeight: 240,
                  objectFit: 'cover',
                  borderRadius: 4,
                  marginBottom: '0.75rem'
                }}
              />
            )}
            <h3 style={{
              margin: '0.5rem 0',
              fontSize: '1.1rem',
              color: '#222'
            }}>
              {g.name}
            </h3>
            <p style={{
              fontSize: '0.9rem',
              color: '#555',
              lineHeight: 1.4,
              height: 'auto',
              overflowY: 'scroll',
              textOverflow: 'ellipsis',
            }}>
              {g.scraped_data.first_paragraph}
            </p>
          </div>
        ))}
      </div>

      {/* pagination dots */}
      <div style={{
        position: 'absolute',
        bottom: 8,
        left: '50%',
        transform: 'translateX(-50%)',
        display: 'flex',
        gap: 6
      }}>
        {games.map((_, i) => (
          <div
            key={i}
            onClick={() => setIdx(i)}
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: i === idx ? '#333' : '#ccc',
              cursor: 'pointer'
            }}
          />
        ))}
      </div>
    </div>
  );
}
