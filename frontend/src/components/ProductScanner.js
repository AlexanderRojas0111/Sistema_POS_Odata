import React from 'react';
import BarcodeReader from 'react-barcode-reader';

export default function ProductScanner({ onScan }) {
  return (
    <BarcodeReader
      onError={console.error}
      onScan={onScan}
    />
  );
} 