import React from 'react';
import jsPDF from 'jspdf';

export default function Ticket({ data }) {
  const handleDownload = () => {
    const doc = new jsPDF();
    doc.text('Ticket de Venta', 10, 10);
    // Agrega más detalles del ticket aquí usando data
    doc.save('ticket.pdf');
  };

  return (
    <div>
      <h3>Ticket generado</h3>
      <button onClick={handleDownload}>Descargar PDF</button>
    </div>
  );
} 