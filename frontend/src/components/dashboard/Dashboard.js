import React, { useState, useEffect } from 'react';
import { Line, Bar, Doughnut, Pie } from 'react-chartjs-2';

const Dashboard = () => {
  const [salesData, setSalesData] = useState([]);
  const [inventoryData, setInventoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [salesRes, inventoryRes] = await Promise.all([
        fetch('/api/v1/ventas/dashboard'),
        fetch('/api/v1/inventario/dashboard')
      ]);
      
      const sales = await salesRes.json();
      const inventory = await inventoryRes.json();
      
      setSalesData(sales);
      setInventoryData(inventory);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Cargando dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1>Dashboard O'Data v2.0.0</h1>
      <div className="dashboard-grid">
        <div className="chart-container">
          <h3>Ventas Diarias</h3>
          <p>Implementar gráficos con Chart.js</p>
        </div>
        <div className="chart-container">
          <h3>Stock por Categoría</h3>
          <p>Implementar gráficos con D3.js</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
