import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav style={{ padding: '1rem', background: '#1976d2', color: 'white' }}>
      <Link to="/" style={{ color: 'white', marginRight: '1rem' }}>Caja</Link>
      <Link to="/inventory" style={{ color: 'white', marginRight: '1rem' }}>Inventario</Link>
      <Link to="/sales" style={{ color: 'white' }}>Ventas</Link>
    </nav>
  );
} 