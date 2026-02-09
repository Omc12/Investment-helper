import { useState } from 'react';
import SearchBox from './SearchBox';

function Navbar({ onSelectStock }) {
  return (
    <nav className="navbar">
      <div className="nav-inner">
        <div className="brand-logo" onClick={() => window.location.reload()} style={{ cursor: 'pointer' }}>
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="32" height="32" rx="6" fill="#00D09C" />
            <path d="M10 22L14 12L18 20L22 8" stroke="#121212" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Groww
        </div>

        <div className="search-bar-container">
          <SearchBox onSelectStock={onSelectStock} />
        </div>

        <div className="nav-actions">
          <a href="#" style={{ fontSize: '15px', fontWeight: 500, color: 'var(--text-primary)' }}>Explore</a>
          <a href="#" style={{ fontSize: '15px', fontWeight: 500, color: 'var(--text-secondary)' }}>Investments</a>
          <div className="nav-avatar">
            OC
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
