import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PosBox from './components/PosBox';
import Inventory from './pages/Inventory';
import Sales from './pages/Sales';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<PosBox />} />
        <Route path="/inventory" element={<Inventory />} />
        <Route path="/sales" element={<Sales />} />
      </Routes>
    </Router>
  );
}

export default App; 