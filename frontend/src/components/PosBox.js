import React, { useState } from 'react';
import api from '../services/api';
import ProductScanner from './ProductScanner';
import Ticket from './Ticket';

export default function PosBox() {
  const [cart, setCart] = useState([]);
  const [ticket, setTicket] = useState(null);

  const handleScan = async (barcode) => {
    // Aquí deberías consultar tu API para obtener el producto por código de barras
    try {
      const res = await api.get(`/products/?barcode=${barcode}`);
      if (res.data) setCart([...cart, res.data]);
    } catch (err) {
      alert('Producto no encontrado');
    }
  };

  const handleSale = async () => {
    // Aquí deberías enviar la venta a tu API
    try {
      const res = await api.post('/sales/', { items: cart });
      setTicket(res.data.ticket);
      setCart([]);
    } catch (err) {
      alert('Error al registrar la venta');
    }
  };

  return (
    <div>
      <h2>Caja - Venta Rápida</h2>
      <ProductScanner onScan={handleScan} />
      <ul>
        {cart.map((item, idx) => (
          <li key={idx}>{item.name} - ${item.price}</li>
        ))}
      </ul>
      <button onClick={handleSale}>Cobrar</button>
      {ticket && <Ticket data={ticket} />}
    </div>
  );
} 