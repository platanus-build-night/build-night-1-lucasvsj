import React from 'react';

export default function GameDetails({ game, onBack }) {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <button
        onClick={onBack}
        style={{
          padding: '0.5rem 1rem',
          marginBottom: '1rem',
          background: '#eee',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        ← Back to Search
      </button>

      <h1 style={{ margin: '0 0 1rem' }}>{game.name}</h1>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
        {/* Landscape image */}
        <img
          src={game.landscapeImageUrl}
          alt={`${game.name} landscape`}
          style={{
            flex: 1,
            width: '100%',
            maxHeight: '300px',
            objectFit: 'cover',
            borderRadius: '8px'
          }}
        />

        {/* Portrait image */}
        <img
          src={game.scraped_data?.image_url}
          alt={`${game.name} portrait`}
          style={{
            width: '200px',
            height: '300px',
            objectFit: 'cover',
            borderRadius: '8px'
          }}
        />
      </div>

      {/* Description section */}
      <section style={{ marginTop: '1.5rem' }}>
        <h2>Description</h2>
        <p style={{ lineHeight: '1.6' }}>{game.scraped_data?.first_paragraph}</p>
      </section>

      {/* Rating section */}
      <section style={{ marginTop: '1.5rem' }}>
        <h2>Rating</h2>
        <p>Metacritic Score: {game.metacritic}</p>
      </section>
    </div>
  );
}
