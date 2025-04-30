import React, { useState, useEffect } from 'react';

export default function Layout({ children }) {
  const [open, setOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Styles
  const sidebarBase = {
    background: '#2c3e50',
    color: 'white',
    transition: 'all 0.3s ease',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    zIndex: 1000,
  };
  const sidebarStyle = isMobile
    ? {
        ...sidebarBase,
        position: 'fixed',
        top: 0,
        left: 0,
        height: '100vh',
        width: open ? '200px' : '0',
      }
    : {
        ...sidebarBase,
        width: open ? '240px' : '60px',
        height: '100vh',
      };

  const overlayStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    background: 'rgba(0,0,0,0.4)',
    zIndex: 900,
  };

  const headerStyle = {
    display: isMobile ? 'flex' : 'none',
    alignItems: 'center',
    background: '#2c3e50',
    color: 'white',
    padding: '0.75rem 1rem',
  };

  const mainContainer = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    marginLeft: isMobile ? 0 : open ? '240px' : '60px',
    transition: 'margin 0.3s ease',
    height: '100vh',
    overflow: 'hidden',
  };

  return (
    <div style={{ position: 'relative', display: 'flex', height: '100vh', fontFamily: 'Arial, sans-serif' }}>
      {/* Sidebar */}
      <aside style={sidebarStyle}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: open || isMobile ? 'space-between' : 'center',
            padding: '1rem',
          }}
        >
          {!isMobile && open && <h2 style={{ margin: 0 }}>GameApp</h2>}
          <button
            onClick={() => setOpen(!open)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              fontSize: '1.5rem',
              lineHeight: 1,
            }}
            aria-label={open ? 'Close menu' : 'Open menu'}
          >
            ☰
          </button>
        </div>
        <nav style={{ flex: 1, display: isMobile && !open ? 'none' : 'block' }}>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            <li style={{ margin: '0.5rem 0' }}>
              <button
                onClick={() => window.location.reload()}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  width: '100%',
                  textAlign: open ? 'left' : 'center',
                  padding: '0.5rem 1rem',
                  fontSize: '1rem',
                }}
              >
                {open || isMobile ? 'Home' : <span role="img" aria-label="home">🏠</span>}
              </button>
            </li>
            <li style={{ margin: '0.5rem 0' }}>
              <button
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  width: '100%',
                  textAlign: open ? 'left' : 'center',
                  padding: '0.5rem 1rem',
                  fontSize: '1rem',
                  opacity: 0.7,
                }}
              >
                {open || isMobile ? 'Settings' : <span role="img" aria-label="settings">⚙️</span>}
              </button>
            </li>
          </ul>
        </nav>
      </aside>

      {/* Overlay for mobile when sidebar open */}
      {isMobile && open && <div style={overlayStyle} onClick={() => setOpen(false)} />}

      {/* Main Content */}
      <div style={mainContainer}>
        <header style={headerStyle}>
          <button
            onClick={() => setOpen(!open)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'white',
              fontSize: '1.5rem',
              marginRight: '1rem',
              cursor: 'pointer',
            }}
            aria-label="Toggle menu"
          >
            ☰
          </button>
          <h1 style={{ margin: 0, fontSize: '1.25rem' }}>GameApp</h1>
        </header>
        <main style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>{children}</main>
      </div>
    </div>
  );
}
